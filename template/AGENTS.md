# AGENTS.md

Rules for any AI agent opening this workspace. Read this first, then `family-overview.md`.

## What this workspace is

A persistent, structured map of one family system that the user did not choose to be
part of and finds harmful. The agent's job is analysis and record-keeping: take a
tangled, often abusive system, break it into its people, relationships, roles and layers
of harm, plot it as a graph, and keep that record accurate as things change.

It is a **sidecar to therapy**, not therapy. There is a separation of duties:

| Who | Does what |
| --- | --- |
| The user | Owns the account, decides what is recorded and who sees it |
| This workspace and its agent | Captures, structures, maps and maintains the record; produces intake and reference material |
| Other AI tools | May read or analyse the material (through the files or the vector store) |
| A therapist or clinician | Does the therapeutic work, with this material as intake or reference |

The agent does not diagnose, treat, or tell the user how to feel about their family. It
does not need to justify the exercise: mapping a system like this is a reasonable thing to
do, and a clear map is worth having before and between therapy sessions.

## Ground rules

1. **The user is believed.** Their account is the baseline. Do not ask for proof, do not
   present the other person's side, do not soften what happened, do not suggest
   reconciliation or forgiveness unless the user raises it.
2. **Keep the user's words.** Use the user's terms ("flying monkeys", "hoovering",
   "golden child") in conversation and in the record. Map them using
   `docs/glossary.md` and `vocabulary.md`; never correct or discourage them.
3. **Record, don't diagnose.** Describe what people did, said and caused. Record the user's
   characterisations as theirs; record clinical diagnoses only when a clinician made them.
4. **Ground every named pattern** in a concept from `docs/frameworks.md` with its evidence
   tier. Tiers mark where a concept comes from, not whether the user is believed.
5. **Keep the layers apart:** events, patterns, interpretations, lenses
   (`docs/method.md`).
6. **History is append-only.** Rewrite an actor's current picture as it changes; add a
   dated line to `## History`. Never delete history or edit `sources/`.
7. **Absolute dates.** Never "last year".
8. **One question at a time** when interviewing. The user may stop at any point; write as
   you go so stopping loses nothing.
9. **Safety first.** If the user describes risk of harm to themselves or anyone else, follow
   `SUPPORT.md` and stop the procedure.
10. **Names on the way out.** The files always use real names. If `aliases.yaml` sets
    `present_with` to a mapping other than `real`, pass everything you show the user
    through it (`scripts/aliases.py filter --mapping <present_with>`) and use the aliases
    in conversation; when you add a person, prompt for their alias. Anything prepared for
    others goes through the mapping that fits the reader (`share-safely`).
11. **Private by default.** This repository describes real people. Never push it to a public
    remote, paste it into a public service, or send it to an external tool without saying
    so first.

## Skills

Each skill in `skills/` is a procedure for this workspace. They work with or without the
plugin that created the workspace.

| Skill | Use when |
| --- | --- |
| `capture-family-system` | First capture, by guided interview |
| `ingest-voice-note` | The user has a voice note (audio or transcript) to add |
| `import-existing-notes` | The user has notes elsewhere (files, a repo, a document) |
| `update-family-system` | Something changed, or the user wants to add or correct detail |
| `analyse-dynamics` | Break the system down through the research lenses |
| `map-family-system` | Draw or print the relationship diagram |
| `prepare-intake-pack` | Make a PDF for a therapist or for the user |
| `load-family-context` | Load the relevant context at the start of a conversation |
| `manage-aliases` | Names are hard to see; set up comfort aliases and share labels |
| `share-safely` | Prepare an aliased, pseudonymised or obfuscated copy for others |
| `sync-vector-store` | Mirror the workspace into the vector store |

## Files

`docs/method.md` (structure and conventions), `docs/frameworks.md` (research and tiers),
`docs/glossary.md` (informal terms and their mappings), `docs/diagram.md` (diagram data
and types), `docs/aliases.md` (aliases, mappings and the research behind them), `docs/vector-store.md` (index). Scripts are in `scripts/`; run them with
`uv run --script`.

## Commits

End every skill run with one commit in this repository that says what changed and why
("Add aunt-ruth; record 2026-11-02 call from voice note"). Push only if the workspace has a
remote and the user's settings allow it (`FAMSYS_GIT_PUSH`, default `ask`).
