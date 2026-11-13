---
name: ingest-voice-note
description: Turn a long voice note (audio or transcript) about family members into updates to the family-system map, keeping the transcript verbatim.
---

# Ingest a voice note

The user records a long, unstructured voice note about their family: a first brain dump,
or an update after something happened. This skill transcribes it if needed, keeps the
transcript verbatim as a source, extracts everything it says about people and
relationships, and applies it to the workspace after the user has seen the changes.

## Load

Work from the workspace root: every command below runs there and uses the workspace's
own `scripts/`.

1. Run `../../scripts/workspace.sh` relative to this skill's directory to find the
   workspace and the overlay folder. No workspace: stop and offer `create-workspace`.
2. Read `profile.env` (`workspace.sh env`) and `ingest-voice-note.md` in the overlay if
   present.
3. Read `AGENTS.md`, `docs/method.md`, `docs/glossary.md`, `vocabulary.md`,
   `family-overview.md` and the frontmatter of every file in `actors/`.

Keys this skill reads:

| Key | Default | Meaning |
| --- | --- | --- |
| `FAMSYS_TRANSCRIBE_CMD` | none | Command that prints a transcript for an audio file: `{audio}` is replaced by the path |
| `FAMSYS_KEEP_AUDIO_IN` | none | Folder to move the original audio to after transcription; never the workspace |
| `FAMSYS_GIT_PUSH` | `ask` | `true`, `false` or `ask` |

## 1. Get the transcript

- **Text or a transcript file given**: use it as is.
- **Audio file given**: in this order, use the first that exists:
  1. `FAMSYS_TRANSCRIBE_CMD` from the profile.
  2. A transcription skill or tool available in this session.
  3. A local `whisper` or `whisper.cpp` CLI, if installed and the machine can run it.
  4. Otherwise ask the user for a transcript; do not install anything unasked.

  Before sending audio to any hosted service, say in one sentence which service will
  receive it. Long recordings: transcribe whole if the tool allows; otherwise split with
  `ffmpeg` into segments and join the text.

## 2. Save the source

Write `sources/<YYYY-MM-DD>-voice-note[-<slug>].md` with the frontmatter in
`docs/method.md` (`kind: voice-note`, the recording date if known, the transcription
tool) and the transcript verbatim below it. Light paragraph breaks are fine; do not
correct, summarise or tidy the words. Transcription errors in names: fix only names
the user confirms. Never commit the audio itself.

## 3. Extract

Read the transcript closely, then build a change list grouped by person:

- **New people** mentioned (proposed slug, relation, generation).
- **Events**: what happened, when (resolve "last week" against the recording date into an
  absolute date), who was involved, a short quote. Each links to the source file.
- **Patterns** the user names or that now rest on two or more events.
- **Roles and terms**: the user's words for people and tactics, mapped with
  `docs/glossary.md`; new terms or new senses go to `vocabulary.md`.
- **Relationships** for the diagram: new ones, or a type that changed (for example
  `distant` to `cutoff`).
- **Changes in contact or status**, with the date.
- **The user's own reflections**, attributed as the user's interpretation, and anything
  about the user's own reactions and strategies for `actors/self.md`.
- **Open questions**: gaps or contradictions with what is already recorded. A difference
  from the existing record is a change to note in History, not a doubt about the user.

## 4. Confirm, then apply

Show the change list compactly: per person, a few lines. Ask once: apply all, or adjust?
Then apply:

- Create new actor files from `actors/_actor-template.md`.
- Add events (newest first) and update the summary, roles, patterns and current state of
  each touched actor.
- Update the `relationships` list and the overview sections affected.
- Add a dated `## History` line to every touched actor and a `## Change log` line to the
  overview naming the source.
- Run `uv run --script scripts/family_map.py all`.

## 5. Commit

`git add -A && git commit -m "Voice note <date>: <one-line summary>"`. Push per
`FAMSYS_GIT_PUSH`. Move the audio to `FAMSYS_KEEP_AUDIO_IN` only if set and the user
agreed.

Offer `analyse-dynamics` if the note changed the picture, and `sync-vector-store` if a
vector store is configured.

## Data storage

Reads `profile.env` and `ingest-voice-note.md` from the overlay folder. Writes the
transcript to `sources/`, updates `actors/`, `family-overview.md` and `vocabulary.md`, and
commits. Audio is never written to the workspace. The transcription route may send audio to
a hosted service; the skill names it before doing so.
