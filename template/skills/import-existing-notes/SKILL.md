---
name: import-existing-notes
description: Import existing notes about a family (files, a repo, documents, old context dumps) into the family-system map, keeping originals.
---

# Import existing notes

The user already has material about their family somewhere: a folder of markdown, an
older context repository, a document, therapy notes they wrote, exported chats. This skill
brings it into the workspace structure without losing or rewriting the originals.

## Load

Work from the workspace root: every command below runs there and uses the workspace's
own `scripts/`.

1. Run `../../scripts/workspace.sh` relative to this skill's directory. No workspace:
   offer `create-workspace` (which can also adopt an existing repository in place).
2. Read `profile.env` and `import-existing-notes.md` in the overlay if present.
3. Read `AGENTS.md`, `docs/method.md`, `docs/glossary.md`, `vocabulary.md`,
   `family-overview.md` and the frontmatter of `actors/*.md`.

## 1. Survey

Ask where the material is, then list it: files, sizes, dates, apparent subject. For a large
corpus, survey file names and first lines only, and confirm the scope before reading
everything. Formats: markdown and text read directly; `.docx`, `.pdf`, `.odt` and HTML via
`pandoc` or `pdftotext` if available.

## 2. Preserve

Copy each original into `sources/` as `YYYY-MM-DD-imported-<slug>.md` (date: the file's own
date if it states one, else its modification date), with `kind: imported` and
`original: <original path or name>` in the frontmatter, body verbatim. If the material is
already inside this repository (an adopted repo), leave it where it is and link to it
instead of copying; record its path in the source frontmatter.

## 3. Map

Work person by person, as in `ingest-voice-note` step 3: people, events with absolute
dates, patterns, roles and the user's terms, relationships, contact status, the user's
reflections. Where the old notes used another structure (one big file, a timeline, a
"people" list), map each part to its place; nothing is dropped. Anything that fits nowhere
goes into the most relevant actor's `Open questions` or the overview, with a link to its
source.

## 4. Confirm, apply, commit

Show the per-person change list; apply on the user's go-ahead (as `ingest-voice-note`
step 4); run `uv run --script scripts/family_map.py all`; add History and Change log
lines naming the imported sources; commit with
`git commit -m "Import: <what was imported>"`. Never delete or move the user's originals
outside the workspace.

## Data storage

Reads `profile.env` and `import-existing-notes.md` from the overlay folder. Reads the
user's material where it lies. Writes copies to `sources/`, updates the workspace files
and commits. Does not modify the original files.
