#!/usr/bin/env bash
set -euo pipefail
project=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
usage() {
 cat <<'HELP'
GranArch — Arch puro com o desktop migrado do GranHat
  ./install.sh --verify                  Verificação local sem instalar
  ./install.sh --plan                    Mostrar pacotes e perfil
  ./install.sh --install                 Instalar em Arch básico (usuário comum)
  ./install.sh --live /mnt USER HOST     Instalar base em partições já montadas (ISO Arch)
Veja README.md antes de usar --live. Não formata nem particiona discos.
HELP
}
case ${1:---help} in
 --verify) exec python3 "$project/scripts/verify.py" ;;
 --plan) cat "$project/manifests/hardware.json" "$project/manifests/packages.txt"; exit ;;
 --live) shift; exec bash "$project/scripts/install-live.sh" "$@" ;;
 --install) [[ $# == 1 ]] || { usage; exit 2; } ;;
 --help|-h) usage; exit ;;
 *) usage; exit 2 ;;
esac
[[ $EUID -ne 0 ]] || { echo 'Execute --install como usuário comum com sudo.' >&2; exit 1; }
source /etc/os-release
[[ $ID == arch && $(uname -m) == x86_64 ]] || { echo 'Destino precisa ser Arch Linux puro x86_64.' >&2; exit 1; }
mapfile -t packages < <(sed '/^[[:space:]]*#/d;/^[[:space:]]*$/d' "$project/manifests/packages.txt")
printf 'Instalação Arch: %s pacotes, Hyprland Lua, Noctalia v5 e perfil pessoal.\n' "${#packages[@]}"
# A full upgrade prevents partial upgrades on an existing Arch installation.
sudo pacman -Syu --needed "${packages[@]}"
python3 "$project/scripts/verify.py"
python3 "$project/scripts/check-versions.py"
sudo python3 "$project/scripts/install-desktop-apps.py" "$(id -un)"
sudo python3 "$project/scripts/configure-system.py" "$(id -un)"
exec bash "$project/scripts/user-install.sh"
