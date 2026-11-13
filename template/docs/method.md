# Method: how this workspace is organised and kept

The workspace is a small set of linked markdown files describing one family system: who
is in it, how each person behaves, and how the system works. The git repository is the
source of truth. A vector store, if used, is a disposable index built from it.

## Layout

```
family-overview.md        the top-level note: the system as a whole
actors/
  _actor-template.md      blank actor file; copy, never edit in place
  self.md                 the user, as a member of the system
  <slug>.md               one file per person
sources/
  YYYY-MM-DD-<slug>.md    raw material, verbatim: voice-note transcripts, imported notes
vocabulary.md             the user's own terms and what they mean by them
aliases.yaml              alias key and mappings (comfort, share, obfuscated)
exports/                  generated diagrams, packs and mapped copies (git-ignored)
docs/                     method and research (this folder)
skills/                   agent skills that operate on this workspace
scripts/                  vector store sync
.family-systems-context   workspace marker (what made it, when)
```

Nothing else is required. Add folders only when a need recurs (for example `letters/`).

## File names and links

- Actor slugs are short, lowercase, hyphenated and **role-based**: `mother.md`,
  `father.md`, `brother-elder.md`, `grandmother-maternal.md`. Names go inside the file.
- The files always use **real names**. Aliases (for the user's comfort, or for sharing)
  live in `aliases.yaml` and are applied only to what is shown or exported; see
  [`aliases.md`](aliases.md).
- Link with relative markdown links so they work on GitHub, in any editor and in Obsidian:
  `[Mother](actors/mother.md)` from the overview, `[Father](father.md)` between actors,
  `[voice note 2026-11-13](../sources/2026-11-13-voice-note.md)` from an actor to a source.
- Every person mentioned in more than passing gets an actor file and a link on first mention
  in each file.

## Layers of a claim

Every statement about a person sits in one of four layers. Keeping them apart is about
precision, not credibility: the user's account is the baseline and is never doubted (see
`frameworks.md`, "Rules that come before any framework"). Separated layers let a therapist,
or another tool, see at a glance what happened, how often, what the user makes of it, and
which clinical concept it corresponds to.

| Layer | Form | Example |
| --- | --- | --- |
| **Event** | Dated, specific, with a source link | 2024-03, at the birthday dinner, said the user "ruined it again" in front of guests ([source](../sources/...)) |
| **Pattern** | A recurring behaviour, with links to two or more events | Public criticism of the user at family occasions (3 events) |
| **Interpretation** | A reading of what the behaviour means or does, attributed | User's reading: the criticism keeps attention off the parents' marriage |
| **Lens** | A named concept from `frameworks.md`, with tier | Detouring (Minuchin, Tier B); scapegoat (user's term, Tier C) |

Rules:

- A pattern needs at least two linked events. Until then it is an event.
- An interpretation always says whose it is: the user's, a therapist's (as reported by the
  user), or the agent's.
- A lens always names its framework and tier.
- Dates are absolute (`2026-11-13`, `2019`, `c. 2005`). Never "last year".
- When the user is unsure of a detail, record the uncertainty ("around 2010, user not sure").

## Updating: dynamics change

Families shift: contact resumes or ends, roles move between siblings, someone dies, a
parent repairs something. The workspace handles this with append-only history:

- The body of an actor file describes the **current** understanding and is rewritten
  as it changes.
- The `## History` section at the end is **append-only**: one dated line per change in
  understanding ("2026-11-13: contact moved from low to no contact after the call on
  2026-11-02; see source"). Nothing is deleted from it.
- `family-overview.md` keeps the same append-only `## Change log`.
- Sources are never edited after they are written.
- Git history is the full record. Each skill run ends in one commit with a message that
  says what changed and why.

## Sources

`sources/` holds raw material verbatim, so every claim can be traced to what the user
actually said or wrote. A source file has frontmatter:

```yaml
---
date: 2026-11-13          # when recorded or written
kind: voice-note | written-note | imported | session-notes | message | other
recorded_by: user
original: <filename of the audio or original file, if kept elsewhere>
transcription: <tool or "user-supplied">
---
```

Audio files are not committed by default (size, and they are more identifying than text).
The user decides where originals live.

## Privacy

The repository describes real people who have not consented to it. It is private by
default and should stay private. Before syncing to a vector store, the user chooses where
the store runs: a local store and a local embedding model keep everything on the machine;
a hosted store or embedding API sends the text to that provider. The sync skill states
which is configured before it runs.

## Safety

This workspace is for difficult material, not emergencies. If the user describes risk of
harm to themselves or anyone else, stop the current procedure and follow `SUPPORT.md`.
Capturing family material can surface strong feelings; any skill may be paused at any point
and resumed later with nothing lost, because each step writes as it goes.
