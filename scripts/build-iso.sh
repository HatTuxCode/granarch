#!/usr/bin/env bash
# Arch build host only; pass a locally built/reviewed Calamares package.
set -euo pipefail
[[ $EUID == 0 && $# == 1 ]] || { echo 'Uso: sudo scripts/build-iso.sh /caminho/calamares-VERSAO-x86_64.pkg.tar.zst' >&2; exit 2; }
source /etc/os-release
[[ $ID == arch ]] || { echo 'Gere a ISO em Arch Linux puro.' >&2; exit 1; }
for command in mkarchiso repo-add bsdtar; do command -v "$command" >/dev/null; done
package=$(realpath -- "$1")
[[ -f $package ]] || exit 1
[[ $(bsdtar -xOf "$package" .PKGINFO | sed -n 's/^pkgname = //p') == calamares ]] || { echo 'Pacote precisa ser calamares.' >&2; exit 1; }
project=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
python3 "$project/scripts/verify.py"
work=$(mktemp -d /var/tmp/granarch-iso.XXXXXXXX)
profile="$work/profile";cp -a /usr/share/archiso/configs/releng "$profile"
repository="$work/repository";mkdir -p "$repository";cp "$package" "$repository/"
repo-add "$repository/granarch-build.db.tar.gz" "$repository/$(basename "$package")"
printf '\n[granarch-build]\nSigLevel = Optional TrustAll\nServer = file://%s\n' "$repository" >> "$profile/pacman.conf"
# The local build repository exists only on the build host and live package transaction.
root="$profile/airootfs"
mkdir -p "$root/opt/granarch" "$root/etc/calamares" "$root/usr/local/bin" "$root/usr/local/libexec" "$root/etc/systemd/system/multi-user.target.wants" "$root/etc/sddm.conf.d" "$root/etc/skel/.config/hypr"
tar -C "$project" --exclude=.git --exclude=.agents --exclude=.codex --exclude=.aws --exclude=dist --exclude=__pycache__ --exclude='*.pyc' -cf - . | tar -C "$root/opt/granarch" -xf -
cp /etc/pacman.conf "$root/opt/granarch/iso/pacman-target.conf"
cp /etc/pacman.conf "$root/etc/pacman.conf"
cp -a "$project/iso/calamares/." "$root/etc/calamares/"
cp -a "$project/iso/live/." "$root/"
python3 - "$profile/packages.x86_64" "$project/manifests/packages.txt" <<'PY'
import sys
from pathlib import Path
p=Path(sys.argv[1]);packages=set(p.read_text().splitlines())
packages.update(line for line in Path(sys.argv[2]).read_text().splitlines() if line and not line.startswith('#'))
packages.update(['calamares','arch-install-scripts','grub','efibootmgr','btrfs-progs','gptfdisk','parted','python-yaml','rsync','squashfs-tools'])
p.write_text('\n'.join(sorted(packages))+'\n')
PY
# Custom profile metadata; the releng bootloader templates remain maintained by Arch.
cat >> "$profile/profiledef.sh" <<'PROFILE'
iso_name="granarch"
iso_label="GRANARCH_$(date +%Y%m)"
iso_publisher="GranArch"
iso_application="Arch Linux + Hyprland + Noctalia + Calamares"
file_permissions+=(
 ["/usr/local/bin/granarch-live-setup"]="0:0:755"
 ["/usr/local/bin/granarch-install-gui"]="0:0:755"
 ["/usr/local/libexec/granarch-calamares"]="0:0:755"
)
PROFILE
# archiso defaults overlay files to 0644, even when Git stores them as executable.
python3 "$project/scripts/export-iso-permissions.py" "$root" >> "$profile/profiledef.sh"
ln -sf /etc/systemd/system/granarch-live.service "$root/etc/systemd/system/multi-user.target.wants/granarch-live.service"
mkdir -p "$project/dist"
printf 'Área de build preservada para diagnóstico: %s\n' "$work"
mkarchiso -v -w "$work/work" -o "$project/dist" "$profile"
sha256sum "$project"/dist/*.iso > "$project/dist/SHA256SUMS"
echo 'ISO gerada; teste a instalação completa numa VM UEFI antes de usar em hardware.'
