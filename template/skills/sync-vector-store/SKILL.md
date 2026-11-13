---
name: sync-vector-store
description: Upsert the family-system git repo into a Qdrant vector store (repo stays source of truth); also query, status and rebuild the index.
---

# Sync the vector store

Mirror the workspace into a Qdrant collection so other agents and tools can retrieve
family context by meaning. The repository is the source of truth; the collection is a
rebuildable index. See `docs/vector-store.md`.

## Load

Work from the workspace root: every command below runs there and uses the workspace's
own `scripts/`.

1. Run `../../scripts/workspace.sh` relative to this skill's directory.
2. Load the profile into the environment for the script:
   `set -a; source <(scripts/workspace.sh env); set +a`. Read `sync-vector-store.md` in
   the overlay if present.

Keys: `FAMSYS_QDRANT_URL` or `FAMSYS_QDRANT_PATH`, `FAMSYS_QDRANT_API_KEY_ENV`,
`FAMSYS_COLLECTION`, `FAMSYS_EMBED_BASE_URL`, `FAMSYS_EMBED_MODEL`,
`FAMSYS_EMBED_API_KEY_ENV` (table and defaults in `docs/vector-store.md`). None set: stop
and offer the plugin's `setup` skill to configure a store.

## Steps

1. **Commit first.** If `git status` shows uncommitted changes, ask whether to commit them;
   the index records the commit it was built from.
2. **Say where the text goes**, in one sentence, from the configuration (see the table in
   `docs/vector-store.md`): e.g. "Embedding with text-embedding-3-small at
   api.openai.com; storing in a local Qdrant folder."
3. **Plan**: `uv run --script scripts/vector_sync.py plan`. Report chunks to embed and to
   delete.
4. **Sync**: `uv run --script scripts/vector_sync.py sync`. If the key lives in a secrets
   manager, run the command through the user's wrapper as their overlay notes describe.
5. **Verify** with a real query, not just the count: pick a person from the overview and
   run `vector_sync.py query "<something recorded about them>" --top 3`; the top hit
   should come from their file. Report the result.

Other commands: `status` (point count), `drop` then `sync` (full rebuild, e.g. after
changing the embedding model, which changes vector size).

## Data storage

Reads `profile.env` and `sync-vector-store.md` from the overlay folder and the workspace
files. Writes to the configured Qdrant collection only. Sends chunk text to the configured
embedding endpoint, which the skill names before syncing.
