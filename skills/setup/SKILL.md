---
name: setup
description: Set up family-systems-context: where the family-data repo lives, git push, voice-note transcription and the vector store. Writes profile.env.
---

# Set up family-systems-context

Write the user's settings to `profile.env` in their overlay folder, asking only for what
cannot be detected. Every key is optional; the skills work with none set.

## Load

1. Run `../../scripts/workspace.sh` relative to this skill's directory. It prints the
   overlay folder, the rule that chose it, whether `profile.env` exists, and any
   workspace it can find.
2. If `profile.env` exists, read it and treat this run as an edit: show current values,
   change only what the user asks.

## Ask

One topic at a time; accept "skip" for any.

1. **Workspace.** If a workspace was found, confirm it. Otherwise ask whether they have one
   already (a path), want one created (hand off to `create-workspace` after setup), or
   will decide later. Key: `FAMSYS_REPO`.
2. **Pushing.** Commit after every change is standard. Push after commits: `ask` (default),
   `true` or `false`. Key: `FAMSYS_GIT_PUSH`.
3. **Voice notes.** Do they record voice notes? If yes, how should audio be transcribed:
   a command they already use (it must print the transcript; `{audio}` is the path), a
   transcription tool their agent already has, or they will supply transcripts. Keys:
   `FAMSYS_TRANSCRIBE_CMD`, `FAMSYS_KEEP_AUDIO_IN` (where originals go; never the repo).
4. **Vector store** (optional). Explain in two lines what it is for (other tools retrieve
   the family context by meaning; the repo stays the source of truth). If wanted:
   - Store: a Qdrant server URL (`FAMSYS_QDRANT_URL`), or a local folder with no server
     (`FAMSYS_QDRANT_PATH`, suggest a folder inside the overlay, e.g. `<overlay>/qdrant`).
     API key: the **name** of the variable holding it (`FAMSYS_QDRANT_API_KEY_ENV`).
   - Embeddings: any OpenAI-compatible endpoint. Offer: OpenAI (default), a local Ollama
     (`http://localhost:11434/v1`, `nomic-embed-text`; nothing leaves the machine), or
     another provider. Keys: `FAMSYS_EMBED_BASE_URL`, `FAMSYS_EMBED_MODEL`,
     `FAMSYS_EMBED_API_KEY_ENV` (a variable name, never the key).
   - Collection name: `FAMSYS_COLLECTION` (default `family-system`).
5. **Secrets route.** If their keys come from a secrets manager or wrapper command, record
   how as a comment line in the profile ("Run scripts through: <wrapper> ..."); the
   skills follow it.

## Write

Write `<overlay>/profile.env`, one `KEY=value` per line, with a comment above each
saying what it does. Never write a secret value. Create the folder if needed. Show the
file and its path. Keys are documented in `reference/profile-keys.md`.

## Verify

- `scripts/workspace.sh` now finds the workspace (if one was given).
- If a vector store was configured: from the workspace root, run
  `set -a; source <(scripts/workspace.sh env); set +a; uv run --script scripts/vector_sync.py status`
  and report the result.

## Data storage

Writes only `<overlay>/profile.env` (overlay resolved by `scripts/workspace.sh`:
`$FAMSYS_HOME`, `$CLAUDE_USER_DATA/family-systems-context/`,
`~/.claude-user-data/family-systems-context/` if that root exists, the XDG
`claude-plugins` root if it exists, else `~/.claude-user-data/family-systems-context/`).
Never writes inside the plugin or under `~/.claude`.
