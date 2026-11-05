#!/usr/bin/env bash
# Arch build host only; pass a locally built/reviewed Calamares package.
set -euo pipefail
[[ $EUID == 0 && $# -ge 3 ]] || { echo 'Uso: sudo scripts/build-iso.sh /caminho/calamares-VERSAO-x86_64.pkg.tar.zst zen-browser-bin-*.pkg.tar.zst disktree-bin-*.pkg.tar.zst' >&2; exit 2; }
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
cp "$project/iso/pacman.conf" "$profile/pacman.conf"
repository="$work/repository";mkdir -p "$repository"
for archive in "$@"; do cp -- "$archive" "$repository/"; done
repo-add "$repository/granarch-build.db.tar.gz" "$repository/"*.pkg.tar.zst
printf '\n[granarch-build]\nSigLevel = Optional TrustAll\nServer = file://%s\n' "$repository" >> "$profile/pacman.conf"
# The local build repository exists only on the build host and live package transaction.
root="$profile/airootfs"
mkdir -p "$root/opt/granarch" "$root/etc/calamares" "$root/usr/local/bin" "$root/usr/local/libexec" "$root/etc/systemd/system/multi-user.target.wants" "$root/etc/sddm.conf.d" "$root/etc/skel/.config/hypr"
tar -C "$project" --exclude=.git --exclude=.agents --exclude=.codex --exclude=.aws --exclude=dist --exclude=__pycache__ --exclude='*.pyc' -cf - . | tar -C "$root/opt/granarch" -xf -
cp "$project/iso/pacman.conf" "$root/opt/granarch/iso/pacman-target.conf"
cp "$project/iso/pacman.conf" "$root/etc/pacman.conf"
cp -a "$project/iso/calamares/." "$root/etc/calamares/"
cp -a "$project/iso/live/." "$root/"
# The live session needs the same palette integration as an installed desktop.
python3 - "$project" "$root" <<'PYLIVE'
from pathlib import Path
import shutil,sys,json,hashlib
project,root=map(Path,sys.argv[1:])
for source in (project/'payload/system').rglob('*'):
    if source.is_file():
        target=root/source.relative_to(project/'payload/system')
        target.parent.mkdir(parents=True,exist_ok=True)
        try:target.write_text(source.read_text().replace('@HOME@','/home/live'))
        except UnicodeError:shutil.copy2(source,target)
        target.chmod(source.stat().st_mode&0o777)
(root/'etc/chromium/policies/managed').mkdir(parents=True,exist_ok=True)
PYLIVE
for unit in gran-browser-theme.path gran-browser-theme.service; do
 ln -sf "/etc/systemd/system/$unit" "$root/etc/systemd/system/multi-user.target.wants/$unit"
done
# Keep the reviewed native desktop packages available for offline installation.
mkdir -p "$root/opt/granarch/iso/packages"
for archive in "${@:2}"; do cp -- "$archive" "$root/opt/granarch/iso/packages/"; done
python3 - "$root/opt/granarch/iso/packages" <<'PYLOCK'
from pathlib import Path
import hashlib,json,sys
folder=Path(sys.argv[1]);records={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.glob('*.pkg.tar.zst')}
(folder/'lock.json').write_text(json.dumps(records,indent=2)+'\n')
PYLOCK
python3 - "$profile/packages.x86_64" "$project/manifests/packages.txt" <<'PY'
import sys
from pathlib import Path
p=Path(sys.argv[1]);packages=set(p.read_text().splitlines())
packages.update(line for line in Path(sys.argv[2]).read_text().splitlines() if line and not line.startswith('#'))
packages.update(['zen-browser-bin','disktree-bin','calamares','arch-install-scripts','grub','efibootmgr','os-prober','btrfs-progs','gptfdisk','parted','python-yaml','rsync','squashfs-tools'])
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
