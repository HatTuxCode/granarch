#!/usr/bin/env bash
set -euo pipefail
[[ $EUID -ne 0 ]] || { echo 'Execute como usuário de destino.' >&2; exit 1; }
project=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
export PATH="$HOME/.local/share/mise/shims:$HOME/.local/bin:$HOME/.local/share/gran/bin:$PATH"
python3 "$project/scripts/apply-home.py"
mkdir -p "$HOME/.local/share/applications"
cat > "$HOME/.local/share/applications/virt-manager.desktop" <<'DESKTOP'
[Desktop Entry]
Type=Application
Name=Gerenciador de máquinas virtuais
Exec=env GTK_THEME=adw-gtk3-dark virt-manager
Icon=virt-manager
Categories=System;
DESKTOP
cat > "$HOME/.local/share/applications/gran-view-image.desktop" <<'DESKTOP'
[Desktop Entry]
Type=Application
Name=Imagens
Exec=gran-view-image %f
Icon=image-x-generic
MimeType=image/png;image/jpeg;image/webp;image/gif;image/bmp;image/tiff;
Categories=Graphics;
DESKTOP
gran-tools-install
python3 "$HOME/.local/share/gran/lib/upstream-apps.py" zen tuios
gran-webapp-install https://grancontrol.app
# Existing shortcut uses this exact deterministic web app ID.
xdg-mime default org.kde.dolphin.desktop inode/directory
for mime in image/png image/jpeg image/webp image/gif image/bmp image/tiff; do
 xdg-mime default gran-view-image.desktop "$mime"
done
fc-cache -f
noctalia config validate "$HOME/.config/noctalia/config.toml"
Hyprland --verify-config --config "$HOME/.config/hypr/hyprland.lua"
echo 'Perfil instalado. Entre pela sessão GranArch no SDDM e execute gran doctor.'
