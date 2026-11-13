---
name: load-family-context
description: Load the user's family-system context (overview, relevant relatives, their terms) at the start of a talk about family or therapy.
---

# Load family context

Use at the start of any conversation where the family matters: preparing for therapy,
processing a call with a parent, deciding how to answer a message. Loads enough context
to talk without making the user re-explain their family, and no more.

## Load

Work from the workspace root: every command below runs there and uses the workspace's
own `scripts/`.

1. Run `../../scripts/workspace.sh` relative to this skill's directory. No workspace:
   say so and offer `create-workspace`.
2. Read `profile.env` and `load-family-context.md` in the overlay if present.

## Steps

1. Read `AGENTS.md` (ground rules), `vocabulary.md`, `aliases.yaml` and
   `family-overview.md`. If `present_with` is not `real`, everything you say or show from
   here on uses that mapping's aliases.
2. Work out who the conversation is about. Read those actors' files in full: `Summary`,
   `Roles`, `Behaviour patterns`, `Current state`, and the five most recent `Events`.
   For everyone else, the members table is enough.
3. If the question is broad ("has this happened before?") and a vector store is
   configured (`FAMSYS_QDRANT_URL` or `FAMSYS_QDRANT_PATH`), run
   `uv run --script scripts/vector_sync.py query "<question>" --top 6` and read the files
   the hits come from. Treat hits as pointers; the files are the record.
4. Give the user a three-to-five-line orientation in their own terms ("Last recorded:
   no contact with your mother since 2026-10-02; your aunt has messaged twice since,
   which you described as hoovering"). Then follow their lead.
5. If the conversation produces something worth recording, offer `update-family-system`
   at the end. Do not write to the workspace during the conversation without asking.

## Data storage

Reads `profile.env` and `load-family-context.md` from the overlay folder and the workspace
files. Writes nothing. A vector query sends the question text to the configured embedding
endpoint.
