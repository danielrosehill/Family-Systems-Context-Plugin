---
name: capture-family-system
description: Map a toxic or abusive family system by guided interview, writing the family overview and one file per person. Use for a first capture.
---

# Capture the family system

Interview the user about their family and write the workspace as you go: the overview,
one actor file per person, and the relationship list that draws the diagram.

## Load

Work from the workspace root: every command below runs there and uses the workspace's
own `scripts/`.

1. Find the workspace and settings: run `../../scripts/workspace.sh` relative to this
   skill's directory. If no workspace is found, stop and offer the plugin's
   `create-workspace` skill (or, without the plugin, copying this template).
2. Read `profile.env` if present (`workspace.sh env`) and `capture-family-system.md` in
   the overlay folder if present; they override the defaults here.
3. Read `AGENTS.md`, `docs/method.md`, `docs/glossary.md` and `vocabulary.md`. Skim
   `docs/frameworks.md` so you can recognise patterns as the user describes them.
4. Read `family-overview.md` and list `actors/`. If people are already recorded, this is
   a continuation: say what is there and ask where to pick up. Use `update-family-system`
   for changes to existing people.

## Before starting

Tell the user, in two or three sentences: you will ask one question at a time, write as
you go, they can stop whenever they like and nothing is lost, and they can say "skip" to
any question. Ask whether hearing or reading the real names is hard for them; if so,
offer `manage-aliases` first, so everything you show them uses aliases while the record
keeps real names. If they would rather talk
than answer questions, offer `ingest-voice-note`: record one long voice note covering
everything, then come back.

## Interview

One question at a time. Follow the user's lead; the order below is a checklist, not a
script. Reflect their words back; never question their account.

1. **Who is in the system.** Parents, step-parents, siblings, grandparents, aunts and
   uncles, partners of family members, anyone else who matters (a family friend, a
   religious figure). For each: relation, rough age or generation, living or deceased.
2. **The user's place.** Birth order, what their role was as a child and is now, in their
   words. Create `actors/self.md` early.
3. **Person by person**, starting with whoever the user names as central: what they are
   like, how they treat the user and others, what they do when challenged, the user's
   words for them, two or three concrete episodes with approximate dates, current contact.
4. **Relationships between others**: who is allied with whom, who is favoured, who is
   blamed, who carries messages, who stays out of it.
5. **The system's rules**: what cannot be said, whose moods govern the house, what happens
   to someone who breaks ranks.
6. **Across generations**: what the parents' own families were like, if known.
7. **Now**: contact decisions, what the user wants from this map (therapy intake, clarity,
   a record), whether they have a therapist.

Use the ACE categories (`docs/frameworks.md`) as a private completeness check: if an area
(neglect, violence between parents, addiction, mental illness, a parent's absence) has not
come up and seems relevant, you may ask about it gently, once. Never compute a score.

## Writing as you go

After each person or major answer, write:

- **Actor file**: copy `actors/_actor-template.md` to `actors/<slug>.md`, fill the
  frontmatter and the sections you have material for. Leave other sections' comments in
  place. Events get absolute dates (or "c. 2005"), and a pattern needs two linked events.
- **Relationships**: append to the `relationships` list in `family-overview.md`
  frontmatter, using the types in `docs/diagram.md`. Put the user's own word in `label`.
- **User's terms**: when the user uses a term not in `docs/glossary.md`, or uses one in
  their own sense, ask once what they mean and add a row to `vocabulary.md`.
- **Source**: if the interview is long, save the user's own key passages verbatim to
  `sources/<date>-capture-interview.md` (kind: `session-notes`) and link events to it.

At natural pauses, and at the end:

1. Fill the overview's `In one paragraph`, `Structure`, `Family rules` and `Where the user
   stands now` from what you have. Leave `Recurring dynamics` and `Layers of harm` for
   `analyse-dynamics` unless the user has spelled them out.
2. Run `uv run --script scripts/family_map.py all` to refresh the members table and map
   and print the PDF. Fix anything `check` reports.
3. Add a line to each touched file's `## History` and to the overview's `## Change log`.
4. Commit in the workspace: `git add -A && git commit -m "Capture: <who was added>"`.
   Push only if `FAMSYS_GIT_PUSH=true`; if `ask` (default) and a remote exists, ask.

## Finish

Show the user the members table and offer, as separate next steps: `analyse-dynamics`,
`map-family-system` (print the diagram), `prepare-intake-pack`.

## Data storage

Reads `profile.env` and `capture-family-system.md` from the overlay folder resolved by
`scripts/workspace.sh`. Writes only inside the workspace: `actors/`, `family-overview.md`,
`vocabulary.md`, `sources/`, `exports/` (git-ignored), and a git commit.
