#!/usr/bin/env bash
# Run by the user in the Arch VM after reviewing the local changes.
set -euo pipefail
[[ $EUID -ne 0 ]] || { echo 'Execute como usuário comum, sem sudo ao redor do script.' >&2; exit 1; }
source /etc/os-release
[[ $ID == arch ]] || { echo 'Este atualizador é somente para o Arch de teste.' >&2; exit 1; }
project=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
python3 "$project/scripts/verify.py"
mapfile -t packages < <(sed '/^[[:space:]]*#/d;/^[[:space:]]*$/d' "$project/manifests/packages.txt")
sudo pacman -Syu --needed "${packages[@]}"
sudo python3 "$project/scripts/install-desktop-apps.py" "$(id -un)"
sudo python3 "$project/scripts/configure-system.py" "$(id -un)" --preserve-locale
bash "$project/scripts/user-install.sh"
export PATH="$HOME/.local/share/mise/shims:$HOME/.local/bin:$HOME/.local/share/gran/bin:$PATH"
# Remove only the former managed shortcut, with its own backup; browser data stays.
if [[ -f $HOME/.local/share/applications/gran-webapp-grancontrol-app-71041194bcba.desktop ]]; then
 gran-webapp-install --remove https://grancontrol.app
fi
systemctl --user daemon-reload
gran-theme-sync
if command -v kbuildsycoca6 >/dev/null; then kbuildsycoca6 --noincremental; fi
sudo systemctl daemon-reload
sudo systemctl restart gran-browser-theme.path
sudo systemctl start gran-browser-theme.service
if [[ -n ${HYPRLAND_INSTANCE_SIGNATURE:-} ]]; then
 hyprctl reload
 hyprctl configerrors
 noctalia msg config-reload
fi
printf 'Atualização aplicada. Feche e reabra Zen, Chromium e Dolphin para testar a aparência.\n'
