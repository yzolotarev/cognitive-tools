#!/bin/bash
# cognitive_trigger.sh — invoke a cognitive operation using current X11 selection.
# Usage: ./cognitive_trigger.sh [compress|relate|predict|reconstruct|map]
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
MODE="${1:-compress}"

export DISPLAY="${DISPLAY:-:0}"
export XAUTHORITY="${XAUTHORITY:-$HOME/.Xauthority}"

TEXT="$(xclip -selection primary -o 2>/dev/null || true)"
if [[ -z "$TEXT" ]]; then
  TEXT="$(xclip -selection clipboard -o 2>/dev/null || true)"
fi

if [[ -z "$TEXT" ]]; then
  exec python3 "$PROJECT_DIR/cognitive_popup.py" <<'EOF'
{"mode":"info","text":"Буфер обмена пуст! Выделите или скопируйте текст."}
EOF
fi

# Use argv instead of shell/heredoc interpolation so arbitrary selected text is safe.
exec python3 "$PROJECT_DIR/cognitive_daemon.py" --trigger-mode "$MODE" --text "$TEXT"
