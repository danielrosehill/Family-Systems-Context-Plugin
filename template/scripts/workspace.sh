#!/usr/bin/env bash
# Locate the family-system workspace and the user's settings overlay.
#
#   scripts/workspace.sh          print workspace root, overlay folder, profile state
#   scripts/workspace.sh root     workspace root only (exit 1 if none)
#   scripts/workspace.sh overlay  overlay folder only
#   scripts/workspace.sh env      profile.env lines (KEY=value), for: set -a; source <(...)
#
# Workspace root: the nearest directory, from $PWD upward, holding the marker
# .family-systems-context. $FAMSYS_REPO from the environment or profile.env is used
# when no marker is found upward.
#
# Overlay (first match wins; Public Plugin, Private Overlay standard):
#   1. $FAMSYS_HOME
#   2. $CLAUDE_USER_DATA/family-systems-context
#   3. ~/.claude-user-data/family-systems-context        if ~/.claude-user-data exists
#   4. ${XDG_DATA_HOME:-~/.local/share}/claude-plugins/family-systems-context   if that root exists
#   5. ~/.claude-user-data/family-systems-context        default
set -euo pipefail

NAME=family-systems-context
MARKER=.family-systems-context
XDG_ROOT="${XDG_DATA_HOME:-$HOME/.local/share}/claude-plugins"

if [[ -n "${FAMSYS_HOME:-}" ]]; then OVERLAY="$FAMSYS_HOME"; RULE=FAMSYS_HOME
elif [[ -n "${CLAUDE_USER_DATA:-}" ]]; then OVERLAY="$CLAUDE_USER_DATA/$NAME"; RULE=CLAUDE_USER_DATA
elif [[ -d "$HOME/.claude-user-data" ]]; then OVERLAY="$HOME/.claude-user-data/$NAME"; RULE="existing ~/.claude-user-data"
elif [[ -d "$XDG_ROOT" ]]; then OVERLAY="$XDG_ROOT/$NAME"; RULE="existing $XDG_ROOT"
else OVERLAY="$HOME/.claude-user-data/$NAME"; RULE=default
fi
PROFILE="$OVERLAY/profile.env"

profile_value() {  # profile_value KEY -> value from profile.env, if any
  [[ -f "$PROFILE" ]] || return 0
  grep -E "^$1=" "$PROFILE" | tail -1 | cut -d= -f2- | sed -e 's/^"//' -e 's/"$//' -e "s|^~|$HOME|"
}

find_root() {
  local d="$PWD"
  while [[ "$d" != "/" ]]; do
    [[ -f "$d/$MARKER" ]] && { echo "$d"; return 0; }
    d=$(dirname "$d")
  done
  local r="${FAMSYS_REPO:-$(profile_value FAMSYS_REPO)}"
  r="${r/#\~/$HOME}"
  if [[ -n "$r" && -f "$r/$MARKER" ]]; then echo "$r"; return 0; fi
  return 1
}

case "${1:-}" in
  root) find_root ;;
  overlay) echo "$OVERLAY" ;;
  env) [[ -f "$PROFILE" ]] && grep -E '^[A-Z_][A-Z0-9_]*=' "$PROFILE" || true ;;
  "")
    echo "workspace: $(find_root || echo 'none found (no marker upward, FAMSYS_REPO unset)')"
    echo "overlay: $OVERLAY ($RULE)"
    echo "profile: $([[ -f "$PROFILE" ]] && echo present || echo missing)"
    ;;
  *) echo "usage: $0 [root|overlay|env]" >&2; exit 2 ;;
esac
