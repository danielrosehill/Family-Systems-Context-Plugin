---
name: create-workspace
description: Create a private git repo for family-system data from the template, scaffold a local folder, or adopt an existing family-notes repo in place.
---

# Create the family-system workspace

Stand up the place the family data lives: a private repository made from the
`Family-System-Context-Template`, a local folder with no remote, or an existing
repository the user already keeps family notes in, adopted in place.

## Load

1. Run `../../scripts/workspace.sh` relative to this skill's directory. If it already
   finds a workspace, say where and ask whether they want a second one; usually they don't.
2. Read `profile.env` and `create-workspace.md` in the overlay if present.

Keys this skill reads:

| Key | Default | Meaning |
| --- | --- | --- |
| `FAMSYS_TEMPLATE` | `danielrosehill/Family-System-Context-Template` | Template repo, so the system can be forked |
| `FAMSYS_OWNER` | the authenticated `gh` user | Where the repo is created |
| `FAMSYS_WORKSPACE_PARENT` | ask | Local parent folder for the clone |
| `FAMSYS_REPO_NAME` | `family-system` | Proposed repository name |

## Choose the route

Ask which applies:

- **New private repo** (recommended): GitHub backing; history and backup.
- **Local folder only**: no remote; or `gh` is unavailable.
- **Adopt an existing repo or folder** that already holds family notes.

## A. New private repository

1. `gh auth status`. Missing or unauthenticated: say so and offer route B.
2. Propose the name; check `gh repo view <owner>/<name>`.
3. **Confirm before creating.** Show the exact command and state that the repository will be
   **private**, will hold detailed personal material about real family members, and will
   live on their GitHub account:
   ```bash
   gh repo create <owner>/<name> --template <FAMSYS_TEMPLATE> --private --clone
   ```
   Run it from the chosen parent folder. If the user asks for public, say once what it
   will contain, then do as they ask.
4. Settle in (below), then commit and push.

## B. Local folder

Assemble the template at the chosen path from the plugin root (two levels up from this
skill): copy `template/` (dotfiles included), then the workspace skills into `skills/`
(every folder in the plugin's `skills/` except `setup` and `create-workspace`), then the
plugin's `scripts/` into `scripts/` (except `sync-from-template.sh`). `git init` there;
settle in; commit. Say what is
lost without a remote (off-machine backup) and that a remote can be added later.

## C. Adopt an existing repository or folder

1. Survey it: list files; never move or rewrite the user's existing files.
2. Add the template's structure alongside, assembled as in route B (`template/`, plus the
   workspace skills and scripts), copying only files and folders that do not already exist: `family-overview.md`, `actors/_actor-template.md`,
   `sources/README.md`, `vocabulary.md`, `docs/`, `skills/`, `scripts/`, `AGENTS.md`,
   `SUPPORT.md`, `.gitignore` entries (append missing lines). If a file of the same name
   exists, keep theirs and put the template's next to it with a `.template` suffix, and
   say so. If they already have a `CLAUDE.md` or `AGENTS.md`, append a short pointer to the
   template's instead of overwriting.
3. Settle in, commit (`git init` first if it is not a repository).
4. Hand off to `import-existing-notes` to map their material in, as a separate step.

## Settle in (all routes)

1. Write the marker `.family-systems-context` at the root, from
   `.family-systems-context.example`: `created` (today, absolute), `subject`, `template`,
   `template_version` (this plugin's version from `.claude-plugin/plugin.json`),
   `backing` (`github` or `local`), `repo` (if any), `workspace_root: .`.
2. Replace `README.md` (routes A and B only) with a short status page: what this
   repository is, that it is private, when it was opened, and a pointer to `AGENTS.md`.
3. Fill `SUPPORT.md` together with the user if they are willing (local crisis line,
   their clinician); skip if not.
4. Offer to save the path to `profile.env` as `FAMSYS_REPO` (through `setup`); never
   write the profile unprompted.
5. Commit: `git add -A && git commit -m "Create family-system workspace"`; push for
   route A.

## Then

Report the local path and URL, and that it is private. Offer the first working step,
separately: `capture-family-system` (interview), `ingest-voice-note` (a long voice note),
or `import-existing-notes`.

## Data storage

Creates the workspace (a new private repository, a local folder, or additions to an
existing repository) and its marker file. Reads `profile.env` and `create-workspace.md`
from the overlay; writes to the overlay only if the user accepts the offer to save.
