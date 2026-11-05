#!/usr/bin/env bash
# Targeted appearance patch; does not reinstall packages or restart applications.
set -euo pipefail
[[ $EUID -ne 0 ]] || { echo 'Execute sem sudo ao redor do script.' >&2; exit 1; }
source /etc/os-release
[[ $ID == arch ]] || { echo 'Somente para a VM Arch.' >&2; exit 1; }
project=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
backup="$HOME/.local/state/gran/backups/colors-$(date -u +%Y%m%dT%H%M%S)-$$"
for relative in .local/share/gran/lib/breeze_icons.py .local/share/gran/lib/dolphin_theme.py .local/share/gran/bin/gran-theme-sync .config/gran/scripts/sync-dolphin-zen.py; do
 mkdir -p "$backup/$(dirname "$relative")" "$HOME/$(dirname "$relative")"
 [[ ! -e $HOME/$relative ]] || cp -a "$HOME/$relative" "$backup/$relative"
 cp -p "$project/payload/home/$relative" "$HOME/$relative"
done
sudo mkdir -p /var/backups/granarch/"$(basename "$backup")"
for relative in gran-theme.cfg defaults/pref/gran-autoconfig.js; do
 if [[ -f /opt/zen-browser-bin/$relative ]]; then
  sudo cp -a "/opt/zen-browser-bin/$relative" "/var/backups/granarch/$(basename "$backup")/$(basename "$relative")"
 fi
 sudo install -Dm644 "$project/payload/system/opt/zen-browser-bin/$relative" "/opt/zen-browser-bin/$relative"
done
export PATH="$HOME/.local/share/gran/bin:$HOME/.local/bin:$PATH"
gran-theme-sync
if command -v kbuildsycoca6 >/dev/null; then kbuildsycoca6 --noincremental; fi
printf 'Feche o Dolphin com Ctrl+Q e encerre o Zen pelo menu Sair. Reabra ambos.\n'
printf 'No Zen, about:config → gran.theme.status deve mostrar loaded.\n'

# Match the source machine's SDDM login; leave the current session running.
if [[ -d /usr/share/sddm/themes/gran ]]; then
 sudo cp -a /usr/share/sddm/themes/gran "/var/backups/granarch/$(basename "$backup")/sddm-gran"
fi
sudo mkdir -p /usr/share/sddm/themes/gran
sudo cp -a "$project/payload/system/usr/share/sddm/themes/gran/." /usr/share/sddm/themes/gran/
sudo chown -R root:root /usr/share/sddm/themes/gran
sudo mkdir -p /etc/sddm.conf.d
printf '[Theme]\nCurrent=gran\n' | sudo tee /etc/sddm.conf.d/95-granarch-theme.conf >/dev/null
printf 'Tema de login preparado para o próximo login; não reinicie o SDDM durante a sessão.\n'
