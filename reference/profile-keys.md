# profile.env keys

`profile.env` lives in the overlay folder (`scripts/workspace.sh overlay` prints it).
Every key is optional. Comments in the file are instructions the skills follow.

| Key | Used by | Default | Meaning |
| --- | --- | --- | --- |
| `FAMSYS_REPO` | all (via `workspace.sh`) | none | Workspace path, used when no marker is found from the current directory upward |
| `FAMSYS_GIT_PUSH` | capture, ingest, import, update, analyse | `ask` | Push after commits: `true`, `false` or `ask` |
| `FAMSYS_TRANSCRIBE_CMD` | ingest-voice-note | none | Command printing a transcript; `{audio}` is the file path |
| `FAMSYS_KEEP_AUDIO_IN` | ingest-voice-note | none | Where original audio goes after transcription (never the workspace) |
| `FAMSYS_TEMPLATE` | create-workspace | `danielrosehill/Family-System-Context-Template` | Template repository |
| `FAMSYS_OWNER` | create-workspace | authenticated `gh` user | Owner for the new repository |
| `FAMSYS_WORKSPACE_PARENT` | create-workspace | ask | Parent folder for the clone |
| `FAMSYS_REPO_NAME` | create-workspace | `family-system` | Proposed repository name |
| `FAMSYS_QDRANT_URL` | sync-vector-store, load-family-context | none | Qdrant server URL |
| `FAMSYS_QDRANT_PATH` | sync-vector-store, load-family-context | none | Local Qdrant folder (embedded mode) |
| `FAMSYS_QDRANT_API_KEY_ENV` | sync-vector-store | none | Name of the variable holding the Qdrant API key |
| `FAMSYS_COLLECTION` | sync-vector-store | `family-system` | Collection name |
| `FAMSYS_EMBED_BASE_URL` | sync-vector-store | `https://api.openai.com/v1` | OpenAI-compatible embeddings endpoint |
| `FAMSYS_EMBED_MODEL` | sync-vector-store | `text-embedding-3-small` | Embedding model |
| `FAMSYS_EMBED_API_KEY_ENV` | sync-vector-store | `OPENAI_API_KEY` | Name of the variable holding the embedding key |

`FAMSYS_HOME` (environment only) overrides the overlay folder itself.

The overlay can also hold `<skill-name>.md` files: private notes for one skill (for
example `prepare-intake-pack.md`: "always prepared for Dr X; leave out my brother"), which
win over the skill's defaults.
