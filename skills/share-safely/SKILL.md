---
name: share-safely
description: Prepare family-system material for semi-trusted or untrusted readers: alias, pseudonymise or obfuscate names, places and details before sharing.
---

# Share safely

Prepare a copy of family-system material for someone the user trusts less than their
therapist, or not at all: a support group, a friend, another AI tool, a forum post. The
record keeps real names; the copy goes through a mapping. Background: `docs/aliases.md`.

## Load

Work from the workspace root: every command below runs there and uses the workspace's
own `scripts/`.

1. Run `../../scripts/workspace.sh` relative to this skill's directory.
2. Read `profile.env` and `share-safely.md` in the overlay if present.
3. Read `docs/aliases.md` and `aliases.yaml`. No aliases yet: run `manage-aliases` first
   (share labels at minimum).

## Steps

1. **Who is it for, and what?** Ask the reader and the material: the whole workspace, one
   person's file, the diagram, an intake pack, or a passage the user wants to post.
2. **Pick the mapping**, and say why in a sentence:
   - semi-trusted (a group, a friend, another AI tool): `share`;
   - untrusted or public: `obfuscated`;
   - the user's own comfort copy: `comfort`.
3. **Check coverage**: `uv run --script scripts/aliases.py check`. Every person in the
   material needs an entry.
4. **Produce it:**
   - whole workspace: `uv run --script scripts/aliases.py render --mapping <m>`
     (to `exports/<m>-<date>/`; add `--with-sources` only if asked);
   - one file or a passage: `uv run --script scripts/aliases.py filter --mapping <m> <file>`
     (or pipe the text in);
   - diagram: `uv run --script scripts/family_map.py pdf --mapping <m>`;
   - intake pack: `uv run --script scripts/intake_pack.py --mapping <m>`.
5. **Review the output yourself** for what a mapping cannot catch, especially for
   `obfuscated`: distinctive events, ages, professions, illnesses, unusual family shapes,
   quotes someone would recognise, names of people not in `aliases.yaml`, places not in
   `other_identifiers`. List each with a suggested generalisation ("a sibling's wedding in
   2019" for a uniquely described wedding). Apply what the user accepts to the **copy**
   only, or add new identifiers to `aliases.yaml` and re-run.
6. **Report** the path, the mapping used, `leftover_names` from `render` (should be empty),
   and one honest line on residual risk: obfuscation reduces, does not remove, the chance
   that someone who knows the family recognises it.
7. **Sending or posting** is the user's act. Do it for them only if asked, and name the
   destination first.

Never include `aliases.yaml` or `exports/alias-key-*` in anything shared.

## Data storage

Reads `profile.env` and `share-safely.md` from the overlay folder, and the workspace.
Writes mapped copies under `exports/` (git-ignored). Edits to `aliases.yaml` only with
the user's agreement.
