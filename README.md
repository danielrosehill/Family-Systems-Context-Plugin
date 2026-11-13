# Family Systems Context

An agent plugin for mapping a **toxic or abusive family system** and keeping that map
as persistent context: one linked markdown file per person, a family overview, roles and
dynamics grounded in family-systems research, a printable relationship diagram, a PDF
intake pack for a therapist, aliases for names that are hard to see, all in a **private
git repository** that is the source of truth, with an optional vector store mirrored
from it.

## What it is, and isn't

Some people find themselves in family systems they did not choose and that harm them:
many people, shifting alliances, roles passed between siblings, tactics that only show
as a pattern over years. This plugin uses what agents are good at, holding a lot of
detail and its relationships, to break such a system down and plot it: who originates
harm, who carries it ("flying monkeys"), who is protected, who absorbs it.

It is a **sidecar to therapy**, not therapy. The agent captures, structures and maps; a
therapist does the therapeutic work, with this as intake or reference material. Other
AI tools can read it too.

- **The user is believed.** Their account is the record.
- **The user's words are kept.** Terms from the informal abuse-recovery literature are
  used as the user uses them, and mapped to research constructs in a glossary a
  clinician can read.
- **Research-grounded.** Bowen family systems theory, Minuchin's structural family
  therapy, genogram conventions, contextual therapy, parentification research, DARVO,
  betrayal trauma, coercive control, ACEs, and the Circumplex and McMaster
  family-functioning models, each with an evidence tier.
- **Names that hurt.** The record keeps real names; aliases are applied to everything
  shown to the user, and pseudonymised or obfuscated copies can be made for others.

## How it is organised

The plugin is public and generic. Your family data lives in a **workspace**: a private
repository created from the public
[Family-System-Context-Template](https://github.com/danielrosehill/Family-System-Context-Template),
which carries its own skills and docs and works with this plugin uninstalled. Your
settings live in an overlay folder outside the plugin (`profile.env`).

```
family-overview.md     the system as a whole; the relationship list that draws the diagram
actors/                one file per person, including self.md for you
sources/               raw material, verbatim (voice-note transcripts, imported notes)
vocabulary.md          your own terms and what you mean by them
aliases.yaml           comfort aliases and share labels
docs/                  method, frameworks, glossary, diagram, aliases, vector store
```

## Skills

**Setting up** (plugin only)

- `setup`: settings: where the workspace is, pushing, voice-note transcription, vector store.
- `create-workspace`: a new private repository from the template, a local folder, or an
  existing family-notes repository adopted in place.

**Getting the family in**

- `capture-family-system`: guided interview, one question at a time, written as it goes.
- `ingest-voice-note`: one long voice note (audio or transcript) in; transcript kept
  verbatim; changes extracted and applied after you see them.
- `import-existing-notes`: notes you already have, mapped in; originals untouched.

**Keeping it current and using it**

- `update-family-system`: incidents, contact changes, role shifts, corrections, with
  dated, append-only history.
- `analyse-dynamics`: the research lenses: layers of harm, structure, triangles, roles,
  parentification, DARVO and gaslighting, loyalties, functioning.
- `map-family-system`: the relationship diagram as a printable PDF and a Mermaid map.
- `prepare-intake-pack`: a PDF for a therapist: diagram, overview, terms mapped to
  research, a section per person.
- `load-family-context`: the right context at the start of a conversation.
- `manage-aliases`: comfort aliases and share labels, with the printed key.
- `share-safely`: aliased, pseudonymised or obfuscated copies for less trusted readers.
- `sync-vector-store`: idempotent upsert into Qdrant (server or local folder) with any
  OpenAI-compatible embeddings endpoint, including local Ollama.

## Installation

```bash
/plugin marketplace add danielrosehill/Claude-Code-Plugins
/plugin install family-systems-context@danielrosehill
```

Then run the `setup` skill, then `create-workspace`.

Requirements: `git`, `gh` (for a GitHub-backed workspace), [`uv`](https://docs.astral.sh/uv/)
for the scripts, Graphviz for the diagram PDF, `pandoc` (3.1.2+) and `typst` for the
intake pack. Vector store: Qdrant, or nothing extra for its embedded local mode, plus an
embeddings endpoint.

## Settings

All optional; documented in [reference/profile-keys.md](reference/profile-keys.md). The
overlay folder resolves, first match wins: `$FAMSYS_HOME`,
`$CLAUDE_USER_DATA/family-systems-context/`, `~/.claude-user-data/family-systems-context/`
if that root exists, `${XDG_DATA_HOME:-~/.local/share}/claude-plugins/family-systems-context/`
if that root exists, else `~/.claude-user-data/family-systems-context/`.
`scripts/workspace.sh` prints which.

## Maintaining

The template repository is canonical for everything under `template/`, the workspace
skills and the scripts. Change them there, then run `scripts/sync-from-template.sh`;
`--check` reports drift. Plugin-owned: `setup`, `create-workspace`, `reference/`, the sync
script.

## Not a crisis service

Every workspace has a `SUPPORT.md`. If you are at risk, contact a person:
<https://findahelpline.com>.

## License

MIT
