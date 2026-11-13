#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6"]
# ///
"""Render the family relationship map.

Reads actor frontmatter (actors/*.md) and the `relationships` list in
family-overview.md, then:

  check     validate slugs and types, print problems (exit 1 if any)
  render    rewrite the members table and Mermaid map inside family-overview.md
  pdf       write exports/family-map-<date>.{dot,svg,pdf} with Graphviz `dot`
  all       check, render, pdf

Usage: family_map.py [check|render|pdf|all] [--root WORKSPACE] [--title TEXT]
Output: one JSON line on stdout describing what was done.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

MARKER = ".family-systems-context"

# type -> (graphviz attrs, mermaid arrow, directed, legend text)
TYPES: dict[str, tuple[str, str, bool, str]] = {
    "close":             ('color="#2e7d32" penwidth=1.5', "---", False, "close"),
    "very-close":        ('color="#2e7d32" penwidth=3', "===", False, "very close"),
    "fused":             ('color="#6a1b9a" penwidth=3', "===", False, "fused / enmeshed"),
    "distant":           ('color="#9e9e9e" style=dashed', "-.-", False, "distant"),
    "conflictual":       ('color="#ef6c00" penwidth=2', "---", False, "conflictual"),
    "fused-conflictual": ('color="#ef6c00" penwidth=3 style=bold', "===", False, "fused and conflictual"),
    "hostile":           ('color="#c62828" penwidth=2', "---", False, "hostile"),
    "abusive":           ('color="#b71c1c" penwidth=3.5', "==>", True, "abusive (label says which kind)"),
    "cutoff":            ('color="#212121" style=dotted penwidth=2 arrowhead=tee dir=both arrowtail=tee', "-.-", False, "cut off"),
    "estranged":         ('color="#757575" style=dotted', "-.-", False, "estranged"),
    "recruits":          ('color="#8e24aa" style=dashed penwidth=2', "-.->", True, "recruits / uses as proxy"),
    "coalition":         ('color="#1565c0" style=dashed penwidth=2', "-.->", True, "coalition (against: named)"),
    "favours":           ('color="#f9a825" penwidth=2.5', "-->", True, "favours (golden child)"),
    "scapegoats":        ('color="#4e342e" penwidth=2.5', "-->", True, "scapegoats / blames"),
    "parentified-by":    ('color="#8d6e63" style=dashed penwidth=2', "-.->", True, "child cares for parent (parentification)"),
    "unknown":           ('color="#bdbdbd" style=dashed', "-.-", False, "unknown"),
}

CONTACT_FILL = {
    "regular": "#e8f5e9", "limited": "#fff8e1", "low": "#fff3e0",
    "no-contact": "#eeeeee", "estranged": "#eeeeee", "n/a": "#ffffff", "": "#ffffff",
}


def find_root(start: Path) -> Path:
    for d in [start, *start.parents]:
        if (d / MARKER).is_file():
            return d
    sys.exit(f"no {MARKER} marker found from {start} upward; pass --root")


def frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        return {}, text
    return (yaml.safe_load(m.group(1)) or {}), m.group(2)


def load(root: Path) -> tuple[dict[str, dict], list[dict], dict]:
    actors: dict[str, dict] = {}
    for p in sorted((root / "actors").glob("*.md")):
        if p.name.startswith("_"):
            continue
        fm, _ = frontmatter(p)
        fm["slug"] = p.stem
        fm.setdefault("name", p.stem.replace("-", " ").title())
        actors[p.stem] = fm
    ov_fm, _ = frontmatter(root / "family-overview.md")
    rels = ov_fm.get("relationships") or []
    return actors, rels, ov_fm


def check(actors: dict, rels: list) -> list[str]:
    problems = []
    if "self" not in actors:
        problems.append("actors/self.md is missing (the user is a member of the system)")
    for i, r in enumerate(rels):
        for key in ("from", "to"):
            if r.get(key) not in actors:
                problems.append(f"relationship {i + 1}: {key} '{r.get(key)}' has no actor file")
        if r.get("type") not in TYPES:
            problems.append(f"relationship {i + 1}: unknown type '{r.get('type')}' (see docs/diagram.md)")
        if r.get("type") == "coalition" and r.get("against") and r["against"] not in actors:
            problems.append(f"relationship {i + 1}: against '{r['against']}' has no actor file")
    return problems


def node_label(a: dict) -> str:
    bits = [str(a.get("name") or a["slug"])]
    if a.get("relation") and a["relation"] != "self":
        bits.append(str(a["relation"]))
    status = str(a.get("status") or "living")
    if status != "living":
        bits.append(status)
    if a.get("contact") and a["contact"] not in ("n/a", ""):
        bits.append(f"contact: {a['contact']}")
    return "\n".join(bits)


def edge_label(r: dict, actors: dict) -> str:
    label = str(r.get("label") or "")
    if r.get("type") == "coalition" and r.get("against") in actors:
        against = actors[r["against"]].get("name") or r["against"]
        label = (label + " " if label else "") + f"against {against}"
    return label


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def to_dot(actors: dict, rels: list, title: str) -> str:
    out = [
        "digraph family {",
        f'  label="{esc(title)}"; labelloc=t; fontsize=20; fontname="Helvetica";',
        '  graph [rankdir=TB, nodesep=0.6, ranksep=0.9, pad=0.4];',
        '  node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=11];',
        '  edge [fontname="Helvetica", fontsize=9];',
    ]
    by_gen: dict[int, list[str]] = {}
    for slug, a in actors.items():
        try:
            gen = int(a.get("generation") or 0)
        except (TypeError, ValueError):
            gen = 0
        by_gen.setdefault(gen, []).append(slug)
        fill = CONTACT_FILL.get(str(a.get("contact") or ""), "#ffffff")
        extra = ""
        if slug == "self":
            fill, extra = "#e3f2fd", " penwidth=2.5"
        if str(a.get("status") or "living") != "living":
            extra += " style=\"rounded,filled,dashed\""
        out.append(f'  "{slug}" [label="{esc(node_label(a))}" fillcolor="{fill}"{extra}];')
    gens = sorted(by_gen)
    for gen in gens:
        out.append("  { rank=same; " + " ".join(f'"{s}";' for s in by_gen[gen]) + " }")
    for upper, lower in zip(gens, gens[1:]):  # stack generations top to bottom
        out.append(f'  "{by_gen[upper][0]}" -> "{by_gen[lower][0]}" [style=invis];')
    for r in rels:
        t = r.get("type")
        if t not in TYPES or r.get("from") not in actors or r.get("to") not in actors:
            continue
        attrs, _, directed, _ = TYPES[t]
        if not directed and "dir=" not in attrs:
            attrs += " dir=none"
        lab = edge_label(r, actors)
        if lab:
            attrs += f' label="{esc(lab)}"'
        out.append(f'  "{r["from"]}" -> "{r["to"]}" [{attrs} constraint=false];')
    used = [t for t in TYPES if t in {r.get("type") for r in rels}]
    if used:
        rows = []
        for t in used:
            attrs, _, directed, text = TYPES[t]
            color = re.search(r'color="([^"]+)"', attrs).group(1)
            stroke = "&#183; &#183; &#183; &#183;" if "dotted" in attrs else ("&#8211; &#8211; &#8211;" if "dashed" in attrs else "&#9473;&#9473;&#9473;&#9473;")
            if "penwidth=3" in attrs:
                stroke = f"<B>{stroke}</B>"
            head = " &#9654;" if directed else ""
            rows.append(f'<TR><TD ALIGN="LEFT"><FONT COLOR="{color}">{stroke}{head}</FONT></TD><TD ALIGN="LEFT">{text}</TD></TR>')
        rows.append('<TR><TD ALIGN="LEFT">dashed box</TD><TD ALIGN="LEFT">deceased</TD></TR>')
        rows.append('<TR><TD ALIGN="LEFT">blue, bold box</TD><TD ALIGN="LEFT">the user</TD></TR>')
        table = '<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="2" COLOR="#bdbdbd"><TR><TD COLSPAN="2"><B>Legend</B></TD></TR>' + "".join(rows) + "</TABLE>>"
        out.append(f'  legend [shape=plaintext style="" fillcolor=none label={table}];')
        out.append(f'  "{by_gen[gens[-1]][0]}" -> legend [style=invis];')
    out.append("}")
    return "\n".join(out) + "\n"


def to_mermaid(actors: dict, rels: list) -> str:
    lines = ["```mermaid", "graph TD"]
    ids = {slug: "n_" + re.sub(r"[^A-Za-z0-9_]", "_", slug) for slug in actors}
    for slug, a in actors.items():
        lab = node_label(a).replace("\n", "<br/>").replace('"', "'")
        lines.append(f'  {ids[slug]}["{lab}"]')
    for r in rels:
        t = r.get("type")
        if t not in TYPES or r.get("from") not in ids or r.get("to") not in ids:
            continue
        arrow = TYPES[t][1]
        lab = f"{t}: {edge_label(r, actors)}" if edge_label(r, actors) else t
        lab = lab.replace('"', "'").replace("|", "/")
        lines.append(f'  {ids[r["from"]]} {arrow}|"{lab}"| {ids[r["to"]]}')
    lines.append("```")
    return "\n".join(lines)


def members_table(actors: dict) -> str:
    rows = ["| Person | Relation | Generation | Status | Contact | Roles |", "| --- | --- | --- | --- | --- | --- |"]
    def gen_key(a):
        try:
            return int(a.get("generation") or 0)
        except (TypeError, ValueError):
            return 0
    for slug, a in sorted(actors.items(), key=lambda kv: (gen_key(kv[1]), kv[0])):
        roles = "; ".join(str(x) for x in (a.get("roles") or []))
        rows.append(
            f"| [{a.get('name') or slug}](actors/{slug}.md) | {a.get('relation', '')} | {a.get('generation', '')} "
            f"| {a.get('status', '')} | {a.get('contact', '')} | {roles} |"
        )
    return "\n".join(rows)


def replace_block(text: str, name: str, body: str) -> str:
    pat = re.compile(rf"(<!-- {name}:start -->)(.*?)(<!-- {name}:end -->)", re.S)
    if not pat.search(text):
        raise SystemExit(f"family-overview.md has no <!-- {name}:start/end --> markers")
    return pat.sub(lambda m: f"{m.group(1)}\n{body}\n{m.group(3)}", text)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", nargs="?", default="all", choices=["check", "render", "pdf", "all"])
    ap.add_argument("--root", type=Path)
    ap.add_argument("--title", default="Family system map")
    ap.add_argument("--mapping", default="real", help="alias mapping for the PDF/SVG (aliases.yaml); the overview always keeps real names")
    args = ap.parse_args()
    root = (args.root or find_root(Path.cwd())).resolve()
    actors, rels, _ = load(root)
    result: dict = {"root": str(root), "actors": len(actors), "relationships": len(rels)}

    problems = check(actors, rels)
    result["problems"] = problems
    if args.cmd == "check":
        print(json.dumps(result))
        sys.exit(1 if problems else 0)

    if args.cmd in ("render", "all"):
        ov = root / "family-overview.md"
        text = ov.read_text(encoding="utf-8")
        text = replace_block(text, "members", members_table(actors))
        text = replace_block(text, "family-map", to_mermaid(actors, rels))
        ov.write_text(text, encoding="utf-8")
        result["rendered"] = str(ov)

    if args.cmd in ("pdf", "all"):
        today = dt.date.today().isoformat()
        exports = root / "exports"
        exports.mkdir(exist_ok=True)
        stem = exports / f"family-map-{today}"
        if args.mapping != "real":
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            from aliases import load_filter
            f = load_filter(root, args.mapping)
            actors = {k: {**a, **{fld: f(str(a[fld])) for fld in ("name", "relation") if a.get(fld)}}
                      for k, a in actors.items()}
            rels = [{**r, **({"label": f(str(r["label"]))} if r.get("label") else {})} for r in rels]
            stem = exports / f"family-map-{args.mapping}-{today}"
        dot_src = to_dot(actors, rels, f"{args.title} ({today})")
        result["mapping"] = args.mapping
        stem.with_suffix(".dot").write_text(dot_src, encoding="utf-8")
        result["dot"] = str(stem.with_suffix(".dot"))
        if shutil.which("dot"):
            for fmt in ("pdf", "svg"):
                subprocess.run(["dot", f"-T{fmt}", "-o", str(stem.with_suffix("." + fmt)), str(stem.with_suffix(".dot"))], check=True)
                result[fmt] = str(stem.with_suffix("." + fmt))
        else:
            result["warning"] = "Graphviz `dot` not found: install graphviz to get the PDF; the .dot file was written"

    print(json.dumps(result))


if __name__ == "__main__":
    main()
