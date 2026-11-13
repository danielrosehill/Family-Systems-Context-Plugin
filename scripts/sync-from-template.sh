#!/usr/bin/env bash
# Refresh this plugin's vendored copy of the Family-System-Context-Template repo.
#
# The template repo is canonical; the copies here are build artefacts. Change a shared
# file in the template FIRST, then run this script. Editing the copy here works once
# and is silently reverted by the next sync.
#
#   scripts/sync-from-template.sh                  pull from GitHub (or the local checkout)
#   scripts/sync-from-template.sh --from ../path   pull from a given checkout
#   scripts/sync-from-template.sh --check          report drift, write nothing (exit 1 on drift)
#
# What is vendored:
#   template/            the whole template (used by create-workspace to scaffold locally)
#   skills/<name>/       every template skill (workspace skills), byte-identical
#   scripts/<file>       every template script, byte-identical
set -euo pipefail
cd "$(dirname "$0")/.."

UPSTREAM_REPO="danielrosehill/Family-System-Context-Template"
DEFAULT_LOCAL="../../Family-System-Context-Template"
PLUGIN_OWNED_SKILLS=(setup create-workspace)
PLUGIN_OWNED_SCRIPTS=(sync-from-template.sh)

src=""; check_only=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --from) src="$2"; shift 2 ;;
    --check) check_only=1; shift ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

tmp=""
if [[ -z "$src" ]]; then
  if [[ -d "$DEFAULT_LOCAL/.git" ]]; then src="$DEFAULT_LOCAL"
  else tmp=$(mktemp -d); git clone -q --depth 1 "https://github.com/$UPSTREAM_REPO" "$tmp"; src="$tmp"; fi
fi
trap '[[ -n "$tmp" ]] && rm -rf "$tmp"' EXIT
[[ -f "$src/family-overview.md" ]] || { echo "not a template checkout: $src" >&2; exit 2; }

is_owned() { local x="$1"; shift; for o in "$@"; do [[ "$x" == "$o" ]] && return 0; done; return 1; }

if (( check_only )); then
  drift=0
  diff -rq --exclude=.git "$src" template >/dev/null || { echo "drift: template/"; diff -rq --exclude=.git "$src" template || true; drift=1; }
  for d in "$src"/skills/*/; do n=$(basename "$d")
    diff -rq "$d" "skills/$n" >/dev/null 2>&1 || { echo "drift: skills/$n"; drift=1; }; done
  for d in skills/*/; do n=$(basename "$d")
    is_owned "$n" "${PLUGIN_OWNED_SKILLS[@]}" || [[ -d "$src/skills/$n" ]] || { echo "orphan: skills/$n"; drift=1; }; done
  for f in "$src"/scripts/*; do n=$(basename "$f")
    cmp -s "$f" "scripts/$n" || { echo "drift: scripts/$n"; drift=1; }; done
  (( drift )) && exit 1
  echo "in sync with $src"; exit 0
fi

rm -rf template && mkdir template
(cd "$src" && tar --exclude=.git -cf - .) | (cd template && tar -xf -)
for d in skills/*/; do n=$(basename "$d"); is_owned "$n" "${PLUGIN_OWNED_SKILLS[@]}" || rm -rf "skills/$n"; done
cp -r "$src"/skills/* skills/
for f in scripts/*; do n=$(basename "$f"); is_owned "$n" "${PLUGIN_OWNED_SCRIPTS[@]}" || rm -f "$f"; done
cp "$src"/scripts/* scripts/
echo "synced from $src"
