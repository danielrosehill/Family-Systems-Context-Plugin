---
name: prepare-intake-pack
description: Build a printable PDF intake pack of the family system (diagram, overview, people, terms mapped to research) for a therapist or the user.
---

# Prepare an intake pack

Produce a PDF a therapist can read before or during a session: a cover with a short
framing note, the relationship diagram, the family overview, the user's terms mapped to
research constructs, and a section per person. It saves the hour that would otherwise go
on reconstructing the family from scratch.

## Load

Work from the workspace root: every command below runs there and uses the workspace's
own `scripts/`.

1. Run `../../scripts/workspace.sh` relative to this skill's directory.
2. Read `profile.env` and `prepare-intake-pack.md` in the overlay if present (a user may
   keep standing preferences there: who it is for, what to leave out).
3. Read `family-overview.md` and the actor frontmatter, so you can describe what will be
   included.

## Steps

1. **Ask scope**, in one message, with defaults:
   - Who it is for (printed on the cover; default none).
   - Which people (default all).
   - Include raw sources such as voice-note transcripts? (default no)
   - Include History logs? (default yes)
   - Names: real (default for the user's own therapist), or a mapping from `aliases.yaml`
     (`comfort`, `share`, `obfuscated`, or one the user defined). Passed as `--mapping`.
2. **Freshen the map** if the data changed since the last render:
   `uv run --script scripts/family_map.py all`.
3. **Build**:
   ```bash
   uv run --script scripts/intake_pack.py [--prepared-for "..."] [--actors a,b] \
     [--with-sources] [--no-history] [--title "..."] [--mapping <name>]
   ```
   Needs `pandoc` (3.1.2+) and `typst`; the diagram needs Graphviz. If one is missing,
   name it and stop rather than producing a partial pack.
4. **Read the PDF before handing it over** (render a page or two to images, or
   `pdftotext`): check the cover, the diagram page and one person section. Fix content
   problems in the workspace files, not in the generated `.typ`.
5. **Hand over** the path in `exports/`. The pack stays out of git; if the user wants a
   dated copy kept, they choose where.

## Notes

- The framing note on the cover says the pack was prepared by the user with an AI
  assistant as intake and reference material, that it is not a clinical assessment, and
  how to read the tiers and layers. Do not add disclaimers beyond it.
- Sending the pack anywhere (email, upload) is the user's call; do it only when asked, and
  name the destination first.

## Data storage

Reads `profile.env` and `prepare-intake-pack.md` from the overlay folder. Writes
`exports/intake-pack-<date>.{typ,pdf}` and refreshes the diagram exports in the workspace.
Nothing leaves the machine.
