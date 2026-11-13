# The vector store

Optional. The git repository is the source of truth; a vector store is a search index
built from it, so other tools and agents can retrieve the relevant parts of the family
context by meaning ("what happens when I set a limit with my mother?") without reading
every file.

## What is indexed

`family-overview.md`, `vocabulary.md`, `actors/*.md` and `sources/*.md`, split by `##`
section into chunks of up to about 1,800 characters. Each chunk starts with its file and
section so it makes sense on its own. Template guidance (HTML comments) and the generated
Mermaid block are skipped. Docs, skills and scripts are not indexed.

Each point carries: `path`, `section`, `kind` (overview, actor, source, vocabulary),
`actor`, `relation`, `date`, `hash` and `commit` (the git commit it was built from).

## How sync works

`scripts/vector_sync.py sync` is idempotent:

1. Chunk the workspace. Each chunk's ID is derived from its file, section and position.
2. Read the hashes already in the collection.
3. Embed and upsert only new or changed chunks.
4. Delete points whose chunk no longer exists (a deleted file or section).

`plan` shows what `sync` would do without calling the embedding API. Deleting the
collection (`drop`) and syncing again rebuilds it exactly.

## Configuration

Keys go in the user's `profile.env` (see the plugin's `setup` skill) or the environment.

| Key | Default | Meaning |
| --- | --- | --- |
| `FAMSYS_QDRANT_URL` | – | Qdrant server, e.g. `http://localhost:6333` |
| `FAMSYS_QDRANT_PATH` | – | Or a local folder: Qdrant's embedded mode, no server needed |
| `FAMSYS_QDRANT_API_KEY_ENV` | – | Name of the variable holding a Qdrant API key |
| `FAMSYS_COLLECTION` | `family-system` | Collection name |
| `FAMSYS_EMBED_BASE_URL` | `https://api.openai.com/v1` | Any OpenAI-compatible embeddings endpoint |
| `FAMSYS_EMBED_MODEL` | `text-embedding-3-small` | Embedding model |
| `FAMSYS_EMBED_API_KEY_ENV` | `OPENAI_API_KEY` | Name of the variable holding the key |

Keys are named by variable, never stored in the workspace or the profile.

## Choosing where the text goes

| Setup | What leaves the machine |
| --- | --- |
| `FAMSYS_QDRANT_PATH` + a local embedding server (Ollama: base URL `http://localhost:11434/v1`, model `nomic-embed-text`) | Nothing |
| `FAMSYS_QDRANT_PATH` + a hosted embedding API | The text of each changed chunk, sent to the embedding provider |
| A hosted Qdrant + a hosted embedding API | The text to the embedding provider, and text plus vectors to the Qdrant host |

The sync skill states which of these is configured before it sends anything.

## Querying

```bash
scripts/vector_sync.py query "how does my brother respond when I mention our mother" --top 6
```

Returns JSON hits with score, path, section and text. Agents should treat hits as
pointers and read the file they come from before relying on them.
