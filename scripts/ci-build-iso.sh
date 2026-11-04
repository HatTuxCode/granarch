#!/usr/bin/env bash
# Runs only as root in the disposable Arch build container, never on the host.
set -euo pipefail
[[ $EUID == 0 ]] || { echo 'Execute dentro do container de build.' >&2; exit 1; }
source /etc/os-release
[[ $ID == arch && -f /.dockerenv ]] || { echo 'Este script exige um container Arch descartável.' >&2; exit 1; }
project=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$project"
pacman-key --init
pacman-key --populate archlinux
# The recipe is repository-owned code. Install build dependencies as root, then
# compile the installer as a dedicated ordinary user, without sudo/NOPASSWD.
source packaging/calamares/PKGBUILD
pacman -Syu --needed --noconfirm base-devel archiso git python python-yaml \
  "${depends[@]}" "${makedepends[@]}"
python3 scripts/verify.py
python3 -m unittest discover -s tests -v
useradd --create-home --shell /bin/bash builder
build=$(mktemp -d /var/tmp/granarch-calamares.XXXXXXXX)
cp packaging/calamares/PKGBUILD "$build/"
chown -R builder:builder "$build"
runuser -u builder -- env MAKEFLAGS="${MAKEFLAGS:--j2}" \
 CMAKE_BUILD_PARALLEL_LEVEL="${CMAKE_BUILD_PARALLEL_LEVEL:-2}" \
 bash -c 'cd "$1"; exec makepkg --noconfirm' bash "$build"
mapfile -t packages < <(find "$build" -maxdepth 1 -type f -name 'calamares-*-x86_64.pkg.tar.zst' ! -name '*-debug-*')
[[ ${#packages[@]} == 1 ]] || { echo 'Build precisa produzir exatamente um pacote Calamares.' >&2; exit 1; }
bash scripts/build-iso.sh "${packages[0]}"
