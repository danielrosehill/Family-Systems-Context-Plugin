# The relationship diagram

The diagram plots the family as a graph: one box per person, one line per relationship,
generations stacked top to bottom, the user highlighted. It is drawn from data, so it
updates whenever the files do.

## Where the data lives

- **People**: the frontmatter of each file in `actors/` (`name`, `relation`, `generation`,
  `status`, `contact`).
- **Relationships**: the `relationships` list in the frontmatter of `family-overview.md`:

```yaml
relationships:
  - {from: mother, to: self, type: abusive, label: emotional}
  - {from: mother, to: aunt-ruth, type: recruits, label: "flying monkey"}
  - {from: mother, to: brother, type: coalition, against: self}
  - {from: father, to: self, type: distant}
```

`from` and `to` are actor slugs (file names without `.md`). `label` is free text and
appears on the line; use it for the user's own word.

## Relationship types

Undirected types follow genogram conventions (McGoldrick et al., 2020). Directed types
read "from does this to or with to" and capture the tactics the user describes.

| Type | Direction | Drawn as | Use for |
| --- | --- | --- | --- |
| `close` | – | green | A warm, supportive relationship |
| `very-close` | – | thick green | Very close |
| `fused` | – | thick purple | Enmeshed: no separateness |
| `distant` | – | grey dashed | Little contact or warmth |
| `conflictual` | – | orange | Ongoing conflict |
| `fused-conflictual` | – | thick orange | Enmeshed and in conflict |
| `hostile` | – | red | Open hostility |
| `abusive` | from → to | thick dark red | Abuse; put the kind in `label` (emotional, physical, sexual, financial) |
| `cutoff` | – | black dotted, barred | Cut off |
| `estranged` | – | grey dotted | Estranged |
| `recruits` | from → to | purple dashed | From uses to as a proxy ("flying monkey") |
| `coalition` | from → to | blue dashed | Allied; add `against: <slug>` |
| `favours` | from → to | gold | Favouritism ("golden child") |
| `scapegoats` | from → to | dark brown | Blame directed at to ("scapegoat") |
| `parentified-by` | from → to | brown dashed | Child (from) cares for parent (to) |
| `unknown` | – | light grey dashed | Not yet known |

Several lines between the same two people are fine and often the point: a mother can both
`favours` one child and form a `coalition` with them.

## Commands

```bash
scripts/family_map.py check     # validate slugs and types
scripts/family_map.py render    # refresh the members table and Mermaid map in the overview
scripts/family_map.py pdf       # exports/family-map-<date>.pdf and .svg (needs Graphviz)
scripts/family_map.py all       # all three
```

Run with `uv run --script scripts/family_map.py ...`, or directly if `uv` is on the path.
The Mermaid map renders on GitHub and in most markdown viewers; the PDF is for printing.
`exports/` is git-ignored: every export can be rebuilt from the files.
