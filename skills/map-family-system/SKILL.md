---
name: map-family-system
description: Draw the family relationship diagram (who is allied, abusive, favoured, scapegoated, recruited) as a printable PDF and a Mermaid map.
---

# Map the family system

Plot the family as a graph: a box per person, generations stacked, the user highlighted,
and a line for each relationship styled by type (abusive, recruits / "flying monkey",
coalition, favours, scapegoats, parentification, cut off and the genogram types). The PDF
is for printing or bringing to therapy; the Mermaid version lives in the overview.

## Load

Work from the workspace root: every command below runs there and uses the workspace's
own `scripts/`.

1. Run `../../scripts/workspace.sh` relative to this skill's directory.
2. Read `profile.env` and `map-family-system.md` in the overlay if present.
3. Read `docs/diagram.md`, the `relationships` list in `family-overview.md` and the
   frontmatter of `actors/*.md`.

## Steps

1. **Check the data**: `uv run --script scripts/family_map.py check`. Fix what it reports:
   a relationship naming a person with no actor file (create the file, or fix the slug),
   an unknown type (map it to the nearest type in `docs/diagram.md`).
2. **Fill gaps** if the user wants a fuller map: walk the members table and ask about
   pairs with no relationship recorded, one at a time. Add entries with the user's own
   word in `label`.
3. **Render**: `uv run --script scripts/family_map.py all --title "<title>"`. Default title
   "Family system map"; use the user's preference if the overlay notes give one. This
   refreshes the overview's members table and Mermaid block and writes
   `exports/family-map-<date>.pdf` and `.svg`. For a PDF with aliases add
   `--mapping <name>` (default: `present_with` from `aliases.yaml` when the map is for the
   user; `share` or `obfuscated` when it is for someone else). The overview always keeps
   real names.
4. **Look at it** before handing it over: open the SVG or render a PNG
   (`dot -Tpng exports/family-map-<date>.dot -o /tmp/preview.png`) and read it. Overlapping
   or unreadable labels: shorten labels, or split a crowded map with a second title
   (e.g. only the actors in one branch, by editing a copy of the .dot).
5. **Hand over** the PDF path. If Graphviz is missing, say so, give the `.dot` path, and
   name the package (`graphviz`) for the user's system.
6. **Commit** the overview changes: `git commit -am "Map <date>"`. Exports are
   git-ignored.

## Data storage

Reads `profile.env` and `map-family-system.md` from the overlay folder. Updates
`family-overview.md` (generated blocks only, plus any relationships the user adds) and
writes `exports/family-map-<date>.{dot,svg,pdf}` in the workspace.
