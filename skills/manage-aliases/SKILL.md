---
name: manage-aliases
description: Give family members aliases so their names stop hurting: suggest or record aliases, set comfort and share mappings, print the alias key.
---

# Manage aliases

For many people, the names of the people in these systems are themselves stressful to
see. This skill sets up aliases: the record keeps real names, and everything shown to the
user, or prepared for others, goes through a mapping. Background and evidence:
`docs/aliases.md`.

## Load

Work from the workspace root: every command below runs there and uses the workspace's
own `scripts/`.

1. Run `../../scripts/workspace.sh` relative to this skill's directory.
2. Read `profile.env` and `manage-aliases.md` in the overlay if present.
3. Read `docs/aliases.md`, `aliases.yaml`, and the frontmatter of `actors/*.md`.

**While this skill runs, refer to people by role ("your mother") unless the user uses
names first.** The point is to spare them the names.

## Steps

1. **Ask what the aliases are for**, briefly: comfort when reading their own material,
   sharing with others, or both. Mention, in a sentence, that renaming can take some of
   the charge out of a name (it borrows from defusion and narrative externalisation; see
   `docs/aliases.md`), with no promise.
2. **Per person**, from the actor files:
   - Collect every way the person is written (`names`): full name, first name, nicknames,
     "Mum", "Mother", a surname if it is used alone. Read the person's actor file and
     sources to find variants the user may not think of; confirm them. If saying the names
     back is hard for the user, list them only once, at the end, for confirmation.
   - **Comfort alias**: ask whether the user has one in mind. If not, offer three or four
     of different kinds (neutral, descriptive, deflating, plain substitute; see
     `docs/aliases.md`). Offer deflating ones only if the user wants that kind. Never name
     a diagnosis. The user's choice stands.
   - **Share label**: a neutral role label ("Parent A", "Sibling 1", "Maternal aunt").
     Propose them all at once; consistent letters across the family.
3. **Other identifiers**: ask about places, schools, workplaces or community names that
   appear in the record and would identify the family; give each a `share` replacement.
4. **Write `aliases.yaml`** (format in `docs/aliases.md`). Set `present_with: comfort` if
   the user wants to see aliases by default. Extra mappings (for example a `therapist`
   field) on request.
5. **Check**: `uv run --script scripts/aliases.py check`. Resolve what it reports (an actor
   with no entry; a variant listed under two people).
6. **Test** on one real file:
   `uv run --script scripts/aliases.py filter --mapping comfort actors/<slug>.md | head -30`;
   show the user the output, not the original. Adjust variants if a name slipped through.
7. **Key**: `uv run --script scripts/aliases.py key` writes `exports/alias-key-<date>.md`;
   offer a PDF (`pandoc ... -t typst | typst compile`) so they can keep a printed key.
8. **Commit** `aliases.yaml`: `git commit -m "Aliases: <what changed>"`.

## From now on

When `present_with` is set to a mapping other than `real`, every skill that shows the user
workspace material passes it through that mapping first (`aliases.py filter --mapping
<present_with>`), and the agent uses aliases in conversation. The user can ask for real
names at any time, for one answer or by setting `present_with: real`.

When a new person is added to the workspace, add them here too: other skills prompt for it
when `aliases.py check` reports a missing entry.

## Data storage

Reads `profile.env` and `manage-aliases.md` from the overlay folder. Writes `aliases.yaml`
in the workspace (private; never exported) and `exports/alias-key-<date>.md`
(git-ignored), and commits.
