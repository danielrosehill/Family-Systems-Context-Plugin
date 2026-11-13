#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6"]
# ///
"""Alias mappings: present or share the family-system record without real names.

The workspace is always written with real names. aliases.yaml defines named mappings
(for example `comfort` for showing material to the user, `share` and `obfuscated` for
other readers); this script applies one on the way out. See docs/aliases.md.

  check                               validate aliases.yaml against the actor files
  filter  --mapping NAME [FILE]       print FILE (or stdin) through the mapping
  render  --mapping NAME [--with-sources]
                                      write a mapped copy of the workspace to
                                      exports/<mapping>-<date>/ and report leftovers
  key                                 write exports/alias-key-<date>.md

Other scripts import `load_filter(root, mapping)` to apply a mapping to diagrams and
intake packs. Output of check, render and key is one JSON line.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Callable

import yaml

MARKER = ".family-systems-context"
KEY_FILE = "aliases.yaml"
FILES = ["family-overview.md", "vocabulary.md", "actors/*.md", "sources/*.md"]

ROLE_WORDS = {"me", "self", "mother", "mum", "mom", "mam", "father", "dad", "brother", "sister",
              "aunt", "uncle", "cousin", "grandmother", "grandfather", "grandma", "grandpa", "gran",
              "nan", "nana", "stepmother", "stepfather", "stepmum", "stepdad", "son", "daughter"}

DEFAULT_MAPPINGS = {
    "real": {"names": None},
    "comfort": {"names": "comfort"},
    "share": {"names": "share", "identifiers": True},
    "obfuscated": {"names": "share", "identifiers": True,
                   "strip": ["emails", "phones", "urls", "full-dates"], "sources": False},
}

STRIP = {  # applied in this order
    "full-dates": (re.compile(r"\b(\d{4})-\d{2}-\d{2}\b"), r"\1"),
    "emails": (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[email]"),
    "urls": (re.compile(r"https?://\S+"), "[link]"),
    "phones": (re.compile(r"(?<![\d-])(\+?\d[\d\s().-]{7,}\d)(?![\d-])"), "[phone]"),
}


def find_root(start: Path) -> Path:
    for d in [start, *start.parents]:
        if (d / MARKER).is_file():
            return d
    sys.exit(json.dumps({"error": f"no {MARKER} marker found from {start} upward; pass --root"}))


def load_key(root: Path) -> dict:
    p = root / KEY_FILE
    if not p.exists():
        return {}
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def mapping_spec(key: dict, name: str) -> dict:
    specs = {**DEFAULT_MAPPINGS, **(key.get("mappings") or {})}
    if name not in specs:
        sys.exit(json.dumps({"error": f"no mapping '{name}'; defined: {sorted(specs)}"}))
    return specs[name]


def name_table(key: dict, spec: dict) -> dict[str, str]:
    """real-name variant -> replacement, for one mapping."""
    field = spec.get("names")
    table: dict[str, str] = {}
    if not field:
        return table
    for person in key.get("people") or []:
        target = person.get(field)
        variants = [str(v) for v in person.get("names") or []]
        if isinstance(target, dict):           # per-variant replacements
            for v in variants:
                if v in target:
                    table[v] = str(target[v])
            default = target.get("*")
            if default:
                for v in variants:
                    table.setdefault(v, str(default))
        elif target:
            for v in variants:
                table[v] = str(target)
    if spec.get("identifiers"):
        for o in key.get("other_identifiers") or []:
            rep = o.get(field) or o.get("replacement") or "[place]"
            table[str(o["real"])] = str(rep)
    return table


def replacer(table: dict[str, str]) -> Callable[[str], tuple[str, int]]:
    """Whole-word, longest-first, single pass, also matching possessives ("Mum's")."""
    if not table:
        return lambda s: (s, 0)
    low = {k.lower(): v for k, v in table.items()}
    keys = sorted(table, key=len, reverse=True)
    pat = re.compile(r"(?<![\w])(" + "|".join(re.escape(k) for k in keys) + r")(?![\w])", re.I)
    return lambda s: pat.subn(lambda m: low[m.group(1).lower()], s)


def load_filter(root: Path, mapping: str) -> Callable[[str], str]:
    """Return a function that applies the named mapping to a string."""
    if mapping == "real":
        return lambda s: s
    key = load_key(root)
    if not key:
        sys.exit(json.dumps({"error": f"{KEY_FILE} not found; the manage-aliases skill creates it"}))
    spec = mapping_spec(key, mapping)
    run = replacer(name_table(key, spec))

    def apply(s: str) -> str:
        s, _ = run(s)
        rules = spec.get("strip") or []
        for rule in [r for r in STRIP if r in rules]:  # fixed order: dates before phones
            rx, rep = STRIP[rule]
            s = rx.sub(rep, s)
        return s
    return apply


def workspace_files(root: Path, with_sources: bool) -> list[Path]:
    out = []
    for pat in FILES:
        if pat.startswith("sources") and not with_sources:
            continue
        out += [p for p in sorted(root.glob(pat)) if not p.name.startswith("_") and p.name != "README.md"]
    return out


def check(root: Path, key: dict) -> list[str]:
    problems = []
    people = key.get("people") or []
    slugs = [p.get("slug") for p in people]
    for a in sorted((root / "actors").glob("*.md")):
        if not a.name.startswith("_") and a.stem not in slugs:
            problems.append(f"actors/{a.name} has no entry in {KEY_FILE}")
    variants = [str(v) for p in people for v in p.get("names") or []]
    dup = sorted({v for v in variants if variants.count(v) > 1})
    if dup:
        problems.append(f"name variants listed under two people: {dup}")
    specs = {**DEFAULT_MAPPINGS, **(key.get("mappings") or {})}
    fields = {s.get("names") for s in specs.values() if s.get("names")}
    for p in people:
        if not p.get("names"):
            problems.append(f"{p.get('slug')}: no names listed")
        for f in sorted(fields):
            if f not in p:
                problems.append(f"{p.get('slug')}: no '{f}' value (mapping falls back to the real name)")
    for s in [s for s in slugs if s]:
        for v in variants:
            if len(v) > 2 and v.lower() not in ROLE_WORDS and v.lower() in s.replace("-", " ").split():
                problems.append(f"actor slug '{s}' contains the real name '{v}'; prefer role-based slugs")
    return problems


def render(root: Path, key: dict, mapping: str, with_sources: bool) -> dict:
    spec = mapping_spec(key, mapping)
    apply = load_filter(root, mapping)
    include_sources = with_sources or spec.get("sources", True)
    today = dt.date.today().isoformat()
    out = root / "exports" / f"{mapping}-{today}"
    if out.exists():
        shutil.rmtree(out)
    files = workspace_files(root, include_sources)
    for f in files:
        dest = out / f.relative_to(root)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(apply(f.read_text(encoding="utf-8")), encoding="utf-8")
    left: dict[str, list[str]] = {}
    table = name_table(key, spec)
    for p in out.rglob("*.md"):
        t = p.read_text(encoding="utf-8")
        for v in [str(v) for person in key.get("people") or [] for v in person.get("names") or []]:
            if v not in table:
                continue
            if re.search(r"(?<![\w])" + re.escape(v) + r"(?![\w])", t, re.I):
                left.setdefault(v, []).append(p.relative_to(out).as_posix())
    return {"export": str(out), "mapping": mapping, "files": len(files),
            "sources_included": bool(include_sources), "leftover_names": left}


def write_key(root: Path, key: dict) -> dict:
    today = dt.date.today().isoformat()
    specs = {**DEFAULT_MAPPINGS, **(key.get("mappings") or {})}
    fields = sorted({s.get("names") for s in specs.values() if s.get("names")})
    lines = [f"# Alias key ({today})", "", "Private: this page links aliases to real people.", "",
             "| Person file | Real names | " + " | ".join(fields) + " |",
             "| --- | --- | " + " | ".join("---" for _ in fields) + " |"]
    for p in key.get("people") or []:
        vals = []
        for f in fields:
            v = p.get(f, "")
            vals.append(", ".join(f"{k} → {x}" for k, x in v.items()) if isinstance(v, dict) else str(v))
        lines.append(f"| {p.get('slug', '')} | {', '.join(map(str, p.get('names') or []))} | " + " | ".join(vals) + " |")
    if key.get("other_identifiers"):
        lines += ["", "| Other identifier | Replacement |", "| --- | --- |"]
        lines += [f"| {o.get('real')} | {o.get('share') or o.get('replacement', '')} |" for o in key["other_identifiers"]]
    out = root / "exports" / f"alias-key-{today}.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"key": str(out)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["check", "filter", "render", "key"])
    ap.add_argument("file", nargs="?", type=Path)
    ap.add_argument("--mapping", default="comfort")
    ap.add_argument("--with-sources", action="store_true")
    ap.add_argument("--root", type=Path)
    a = ap.parse_args()
    root = (a.root or find_root(Path.cwd())).resolve()
    key = load_key(root)
    if a.cmd == "filter":
        text = a.file.read_text(encoding="utf-8") if a.file else sys.stdin.read()
        sys.stdout.write(load_filter(root, a.mapping)(text))
        return
    if not key:
        sys.exit(json.dumps({"error": f"{KEY_FILE} not found; the manage-aliases skill creates it"}))
    if a.cmd == "check":
        probs = check(root, key)
        print(json.dumps({"problems": probs, "people": len(key.get("people") or [])}))
        sys.exit(1 if probs else 0)
    if a.cmd == "render":
        print(json.dumps(render(root, key, a.mapping, a.with_sources)))
    if a.cmd == "key":
        print(json.dumps(write_key(root, key)))


if __name__ == "__main__":
    main()
