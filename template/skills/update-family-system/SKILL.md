---
name: update-family-system
description: Record a family change (incident, contact change, role shift, death, correction) in actor files and overview, with dated history.
---

# Update the family system

Family dynamics move. This skill records a change: a new incident, a call or message, a
change in contact, a role passing from one sibling to another, a death, a reconciliation,
a detail the user wants to add or correct.

## Load

Work from the workspace root: every command below runs there and uses the workspace's
own `scripts/`.

1. Run `../../scripts/workspace.sh` relative to this skill's directory; no workspace,
   stop and offer `create-workspace`.
2. Read `profile.env` and `update-family-system.md` in the overlay if present.
3. Read `AGENTS.md`, `docs/method.md`, `docs/glossary.md`, `vocabulary.md`,
   `family-overview.md`, and the actor files of everyone the update concerns.

For a long spoken update, use `ingest-voice-note` instead; for a batch of files,
`import-existing-notes`.

## Steps

1. **Take the update** in the user's words. Ask only what is needed to record it: who, when
   (absolute date), what was said or done. One question at a time.
2. **Keep the words.** If the user wants the raw account kept, or it is longer than a few
   lines, save it verbatim as `sources/<date>-<slug>.md` (`kind: written-note` or
   `message`) and link to it.
3. **Apply** to each affected actor file:
   - Add the event under `## Events` (newest first), with its source link.
   - Rewrite `Summary`, `Roles`, `Behaviour patterns`, `Current state` and frontmatter
     (`contact`, `status`, `roles`, `updated`) so they describe the present.
   - Append one dated line to `## History` saying what changed and why. Never delete
     History lines.
4. **Relationships**: change or add entries in the overview's `relationships` list. For a
   change of type, keep the new type in the list and record the old one in both actors'
   History ("2026-11-13: brother to self moved from close to distant after ...").
5. **Overview**: update affected sections and append to `## Change log`.
6. **Corrections**: if the user corrects an earlier record, change it and note the
   correction in History. A correction is the user refining their account; record it
   plainly, without comment.
7. Run `uv run --script scripts/family_map.py all`.
8. Commit: `git add -A && git commit -m "Update <date>: <summary>"`. Push per
   `FAMSYS_GIT_PUSH` (default `ask`).

## Data storage

Reads `profile.env` and `update-family-system.md` from the overlay folder. Writes only
inside the workspace (`actors/`, `family-overview.md`, `vocabulary.md`, `sources/`,
`exports/`) and commits.
