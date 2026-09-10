#!/bin/bash
set -euo pipefail

PROJECT_DIR="${HOME}/projects/cognitive-layer"
SERVICE_DIR="${HOME}/.config/systemd/user"

sudo pacman -S --needed python-xlib python-gobject gtk3 xclip xdotool

mkdir -p "$PROJECT_DIR" "$SERVICE_DIR"
cp cognitive_daemon.py cognitive_popup.py cognitive_trigger.sh cognitive-tools.service "$PROJECT_DIR/"
chmod +x "$PROJECT_DIR/cognitive_daemon.py" "$PROJECT_DIR/cognitive_popup.py" "$PROJECT_DIR/cognitive_trigger.sh"
cp cognitive-tools.service "$SERVICE_DIR/"

systemctl --user daemon-reload
systemctl --user enable --now cognitive-tools.service
systemctl --user --no-pager status cognitive-tools.service
