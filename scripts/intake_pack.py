#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6"]
# ///
"""Build a printable intake pack (PDF) from the workspace, for a therapist or for the user.

Contents, in order: cover and framing note, the relationship diagram, the family
overview, the user's vocabulary, the glossary rows for terms the workspace uses, one
section per actor (the user last), and optionally the raw sources.

Usage:
  intake_pack.py [--root WS] [--actors mother,father] [--with-sources] [--no-history]
                 [--title TEXT] [--prepared-for TEXT]

Needs pandoc (3.1.2 or later, for its Typst writer) and typst. Runs family_map.py first
for the diagram if Graphviz is available. Writes exports/intake-pack-<date>.pdf and the
intermediate .typ next to it. Prints one JSON line.
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
HERE = Path(__file__).resolve().parent

FRAMING = """\
This document was prepared by the person it concerns, working with an AI assistant, as
reference and intake material for therapy. It is not a clinical assessment and makes no
diagnosis of anyone.

It records the family system as the person experienced it. Their account is the baseline.
Their own words for what happened are kept as they used them; where a term comes from the
informal recovery literature, the glossary section maps it to the nearest clinical or
research construct, with an evidence tier:

- **Tier A**: empirically studied construct with validated measures.
- **Tier B**: established clinical theory with partial empirical support.
- **Tier C**: practice or popular vocabulary.

Statements about each person are kept in layers: dated **events**, **patterns** that rest on
two or more events, **interpretations** attributed to whoever made them, and named
**lenses** from family-systems research (Bowen, Minuchin, genogram conventions and others).
"""


def find_root(start: Path) -> Path:
    for d in [start, *start.parents]:
        if (d / MARKER).is_file():
            return d
    sys.exit(json.dumps({"error": f"no {MARKER} marker found from {start} upward; pass --root"}))


def split_fm(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        return {}, text
    return (yaml.safe_load(m.group(1)) or {}), m.group(2)


def clean(body: str, drop_history: bool) -> str:
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    body = re.sub(r"```mermaid.*?```", "", body, flags=re.S)
    body = re.sub(r"\[([^\]]+)\]\((?!https?:)[^)]*\)", r"\1", body)  # local links -> text
    body = re.sub(r"^- \*\*[^*]+\*\*[^:\n]*:\s*$\n?", "", body, flags=re.M)  # unfilled "- **X**:" items
    body = re.sub(r"^The family system as a whole\..*?\n\n", "", body, flags=re.S | re.M)  # workspace navigation
    if drop_history:
        body = re.sub(r"\n## (History|Change log)\n.*?(?=\n## |\Z)", "\n", body, flags=re.S)
    # drop headings left with nothing under them
    body = re.sub(r"\n(##+ [^\n]+)\n\s*(?=\n##+ |\Z)", "\n", body)
    return body.strip()


def demote(body: str, levels: int = 1) -> str:
    return re.sub(r"^(#+) ", lambda m: "#" * (len(m.group(1)) + levels) + " ", body, flags=re.M)


def used_glossary_rows(root: Path, corpus: str) -> list[str]:
    gloss = root / "docs" / "glossary.md"
    if not gloss.exists():
        return []
    rows, low = [], corpus.lower()
    for line in gloss.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\| \*\*([^*]+)\*\*([^|]*)\|([^|]*)\|([^|]*)\|", line)
        if not m:
            continue
        names = [m.group(1)] + [n.strip() for n in m.group(2).split(",") if n.strip()]
        if any(n.lower() in low for n in names):
            rows.append(f"| **{m.group(1)}** | {m.group(3).strip()} | {m.group(4).strip()} |")
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path)
    ap.add_argument("--actors", help="comma-separated actor slugs (default: all)")
    ap.add_argument("--with-sources", action="store_true")
    ap.add_argument("--no-history", action="store_true")
    ap.add_argument("--title", default="Family system: intake and reference pack")
    ap.add_argument("--prepared-for", default="")
    ap.add_argument("--mapping", default="real", help="alias mapping from aliases.yaml (comfort, share, obfuscated, ...)")
    args = ap.parse_args()

    for tool in ("pandoc", "typst"):
        if not shutil.which(tool):
            sys.exit(json.dumps({"error": f"{tool} not found; install it to build the PDF"}))

    root = (args.root or find_root(Path.cwd())).resolve()
    today = dt.date.today().isoformat()
    exports = root / "exports"
    exports.mkdir(exist_ok=True)

    diagram = None
    if shutil.which("dot"):
        r = subprocess.run([sys.executable, str(HERE / "family_map.py"), "pdf", "--root", str(root), "--mapping", args.mapping],
                           capture_output=True, text=True)
        if r.returncode == 0:
            svg = json.loads(r.stdout.strip().splitlines()[-1]).get("svg")
            diagram = Path(svg) if svg else None

    parts: list[str] = []
    _, ov = split_fm((root / "family-overview.md").read_text(encoding="utf-8"))
    parts.append(demote(clean(ov, args.no_history), 0))

    voc = root / "vocabulary.md"
    if voc.exists():
        _, vb = split_fm(voc.read_text(encoding="utf-8"))
        vb = clean(vb, False)
        if vb.count("\n|") > 2:  # has rows beyond the header
            parts.append(vb)

    wanted = [s.strip() for s in args.actors.split(",")] if args.actors else None
    actor_files = [p for p in sorted((root / "actors").glob("*.md")) if not p.name.startswith("_")]
    actor_files.sort(key=lambda p: p.stem == "self")  # the user last
    actor_md = []
    for p in actor_files:
        if wanted and p.stem not in wanted:
            continue
        fm, body = split_fm(p.read_text(encoding="utf-8"))
        meta = ", ".join(str(x) for x in [fm.get("relation"), fm.get("status"),
                                           f"contact: {fm['contact']}" if fm.get("contact") else None] if x)
        body = clean(body, args.no_history)
        body = re.sub(r"^# .*\n?", "", body)
        actor_md.append(f"## {fm.get('name') or p.stem}\n\n*{meta}*\n\n{demote(body)}")
    if actor_md:
        parts.append("# People in the system\n\n" + "\n\n".join(actor_md))

    corpus = "\n".join(parts)
    rows = used_glossary_rows(root, corpus)
    if rows:
        parts.insert(1, "# Terms used, and what they map to\n\n| Term | What it means here | Research mapping |\n| --- | --- | --- |\n" + "\n".join(rows))

    if args.with_sources:
        src = []
        for p in sorted((root / "sources").glob("*.md")):
            if p.name == "README.md":
                continue
            fm, body = split_fm(p.read_text(encoding="utf-8"))
            src.append(f"## {p.stem}\n\n*{fm.get('kind', '')}, {fm.get('date', '')}*\n\n{demote(clean(body, False))}")
        if src:
            parts.append("# Sources\n\n" + "\n\n".join(src))

    md = "\n\n".join(parts)
    framing = FRAMING
    if args.mapping != "real":
        sys.path.insert(0, str(HERE))
        from aliases import load_filter
        md = load_filter(root, args.mapping)(md)
        framing += "\nNames of people (and, where set, places) in this document are aliases.\n"
    body_typ = subprocess.run(["pandoc", "-f", "markdown-implicit_figures", "-t", "typst"],
                              input=md, capture_output=True, text=True, check=True).stdout
    framing_typ = subprocess.run(["pandoc", "-f", "markdown", "-t", "typst"],
                                 input=framing, capture_output=True, text=True, check=True).stdout

    def tstr(s: str) -> str:
        return s.replace("\\", "\\\\").replace('"', '\\"')

    diagram_typ = ""
    if diagram and diagram.exists():
        diagram_typ = (f'#pagebreak()\n= Relationship map\n#align(center)[#image("{diagram.name}", '
                       f'width: 100%, height: 85%, fit: "contain")]\n')
    doc = f"""#set document(title: "{tstr(args.title)}")
#set page(paper: "a4", margin: 2cm, numbering: "1",
  footer: context [#set text(8pt, fill: gray); Private and confidential #h(1fr) #counter(page).display()])
#set text(font: ("Libertinus Serif", "New Computer Modern"), size: 10.5pt)
#set heading(numbering: none)
#show heading.where(level: 1): it => [#pagebreak(weak: true) #it]
#set table(stroke: 0.5pt + gray, inset: 5pt)
#show table: set text(9pt)
#show link: it => it.body

#align(center + horizon)[
  #text(22pt, weight: "bold")[{tstr(args.title)}]
  #v(0.6em)
  #text(12pt)[{today}{" · Prepared for " + tstr(args.prepared_for) if args.prepared_for else ""}]
  #v(2em)
  #block(width: 85%)[#set align(left); #set text(9.5pt)
{framing_typ}
  ]
]
#pagebreak()
#outline(depth: 2)
{diagram_typ}
{body_typ}
"""
    suffix = "" if args.mapping == "real" else f"-{args.mapping}"
    typ = exports / f"intake-pack{suffix}-{today}.typ"
    pdf = typ.with_suffix(".pdf")
    typ.write_text(doc, encoding="utf-8")
    r = subprocess.run(["typst", "compile", str(typ), str(pdf)], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(json.dumps({"error": "typst compile failed", "stderr": r.stderr[-2000:], "typ": str(typ)}))
    print(json.dumps({"pdf": str(pdf), "typ": str(typ), "diagram": str(diagram) if diagram else None,
                      "actors": len(actor_md), "glossary_terms": len(rows), "sources": args.with_sources}))


if __name__ == "__main__":
    main()
