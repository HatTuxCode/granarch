#!/usr/bin/env bash
# Update appearance, native bar and OpenCode in an existing Gran installation.
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
[[ $EUID -ne 0 ]] || { echo 'Execute como usuário comum, sem sudo no comando inicial.' >&2; exit 1; }
[[ -f $HOME/.local/share/gran/version ]] || { echo 'Instale o GranArch primeiro.' >&2; exit 1; }
sudo pacman -Syu --needed extra/fastfetch extra/eza extra/fzf extra/bat extra/zoxide extra/tmux extra/neovim core/openssh core/file extra/btop
python "$ROOT/scripts/apply-appearance.py" --home "$HOME"
bash "$ROOT/scripts/repair-opencode.sh"
python "$ROOT/scripts/apply-shortcuts.py" --home "$HOME"
