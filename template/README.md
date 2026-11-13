# Family System Context Template

A template repository for mapping a **toxic or abusive family system** with an AI agent:
one linked markdown file per person, a family overview, a relationship diagram you can
print, and an optional vector index, all kept in a **private** git repository that is the
source of truth.

[![Use this template](https://img.shields.io/badge/Use-this%20template-green?style=flat&logo=github)](https://github.com/danielrosehill/Family-System-Context-Template/generate)
[![Plugin](https://img.shields.io/badge/Plugin-family--systems--context-blue?style=flat&logo=github)](https://github.com/danielrosehill/Family-Systems-Context-Plugin)

## What it is for

Some people grow up in family systems they did not choose and that harm them. Making sense
of such a system is hard: many people, shifting alliances, roles that move between
siblings, tactics that only show up as a pattern over years. This workspace lets an agent
do what agents are good at, holding a lot of detail and its relationships, and plot it:
who originates harm, who carries it, who is protected, who absorbs it.

It is a **sidecar to therapy**, not therapy. The agent captures, structures and maps; a
therapist does the therapeutic work, with this as intake or reference material. Other AI
tools can read it too, through the files or the vector index.

Three commitments shape it:

- **The user is believed.** Their account is the record; the agent does not second-guess it.
- **The user's words are kept.** Terms from the informal abuse-recovery literature
  ("flying monkeys", "hoovering", "golden child") are used as the user uses them, and mapped
  to research constructs in a [glossary](docs/glossary.md) so a clinician can read them.
- **Grounded in research.** Patterns are named with concepts from Bowen family systems
  theory, Minuchin's structural family therapy, genogram conventions, contextual therapy,
  parentification research, DARVO, coercive control and validated family-functioning
  models, each with an evidence tier ([frameworks](docs/frameworks.md)).

## Layout

```
family-overview.md     the system as a whole; relationship list that draws the diagram
actors/                one file per person, including self.md for the user
sources/               raw material, verbatim (voice-note transcripts, imported notes)
vocabulary.md          the user's own terms and what they mean by them
aliases.yaml           alias key: comfort aliases and share labels, applied on the way out
docs/                  method, frameworks, glossary, diagram, vector store
skills/                agent skills for this workspace
scripts/               diagram, intake pack, vector sync, workspace locator
SUPPORT.md             what to do if things are acute
```

## Ways in

- **Interview**: `capture-family-system` asks one question at a time and writes as it goes.
- **Voice note**: record one long voice note covering everyone; `ingest-voice-note`
  transcribes it, keeps the transcript verbatim and turns it into updates.
- **Existing notes**: `import-existing-notes` maps a folder, repo or document in.

Then `update-family-system` as things change, `analyse-dynamics` for the research lenses,
`map-family-system` for the printable diagram, `prepare-intake-pack` for a PDF to give a
therapist, `load-family-context` at the start of a conversation, and `sync-vector-store`
for the optional Qdrant index.

**Names that hurt.** The record keeps real names, but `manage-aliases` lets the user give
everyone an alias, so whatever the agent shows them uses the alias instead; the idea
borrows from cognitive defusion and narrative externalisation
([aliases](docs/aliases.md)). `share-safely` produces pseudonymised or obfuscated copies
for less trusted readers, and the diagram and intake pack take any mapping.

## Using it

With the [plugin](https://github.com/danielrosehill/Family-Systems-Context-Plugin), run
its `create-workspace` skill: it creates a private repository from this template, or
adopts a repository you already have.

Without the plugin: create a **private** repository from this template, clone it, and
open it with your agent. `AGENTS.md` and `skills/` make it self-running.

Requirements: `git`; [`uv`](https://docs.astral.sh/uv/) for the scripts; Graphviz for the
diagram PDF; `pandoc` and `typst` for the intake pack; Qdrant (a server, or none: the
embedded local mode) and an OpenAI-compatible embeddings endpoint for the vector index.

## Not a crisis service

If you are at risk, see [SUPPORT.md](SUPPORT.md).

## License

MIT
