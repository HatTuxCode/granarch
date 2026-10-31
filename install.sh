#!/usr/bin/env bash
# GranArch post-install. Default execution displays a plan without host changes.
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
MODE=plan
CHANGE_SHELL=1
ENABLE_SERVICES=1
INSTALL_YARU=1
CONFIGURE_BOOT=1
CONFIGURE_LOGIN=1
AUTOLOGIN=1
die() { printf 'Erro: %s\n' "$*" >&2; exit 1; }
usage() {
  cat <<'EOF'
GranArch — desktop Gran sobre Arch Linux enxuto
  bash install.sh                     Prévia; não altera o sistema
  bash install.sh --install           Pós-instalador interativo
  bash install.sh --verify            Conferir snapshot
  bash install.sh --no-change-shell   Preservar shell de login
  bash install.sh --no-services       Não habilitar rede/Bluetooth
  bash install.sh --no-yaru           Não compilar ícones/cursor Yaru
  bash install.sh --no-boot           Preservar configuração visual do bootloader
  bash install.sh --no-login          Não configurar SDDM
  bash install.sh --no-autologin      Exigir login SDDM em vez de entrada automática
Execute --install como usuário comum com sudo, no Arch instalado.
O script não adiciona repositórios/chaves/mirrors nem troca o bootloader ou as partições.
EOF
}
for argument in "$@"; do
  case "$argument" in
    --install) MODE=install ;;
    --verify) MODE=verify ;;
    --dry-run) MODE=plan ;;
    --no-change-shell) CHANGE_SHELL=0 ;;
    --no-services) ENABLE_SERVICES=0 ;;
    --no-yaru) INSTALL_YARU=0 ;;
    --no-boot) CONFIGURE_BOOT=0 ;;
    --no-login) CONFIGURE_LOGIN=0 ;;
    --no-autologin) AUTOLOGIN=0 ;;
    --help|-h) usage; exit 0 ;;
    *) die "Opção desconhecida: $argument" ;;
  esac
done
[[ -f $ROOT/snapshot/SHA256SUMS ]] || die 'Snapshot ausente.'
verify() { (cd "$ROOT/snapshot" && sha256sum --quiet -c SHA256SUMS); }
if [[ $MODE == verify ]]; then verify; echo 'Snapshot Gran íntegro.'; exit 0; fi
mapfile -t PACKAGES < <(sed -e 's/#.*//' -e '/^[[:space:]]*$/d' "$ROOT/manifests/packages.txt")
NOTEBOOK_PACKAGES=()
if grep -qi asus /sys/class/dmi/id/sys_vendor 2>/dev/null; then NOTEBOOK_PACKAGES+=(extra/asusctl); fi
if grep -q GenuineIntel /proc/cpuinfo 2>/dev/null; then NOTEBOOK_PACKAGES+=(extra/thermald); fi
cat <<EOF

GranArch — plano de instalação
Desktop: Hyprland + Quickshell de core/extra oficiais do Arch.
Personalização: Nord, sua barra, gestos e todos os módulos de atalhos originais.
Comandos e caminhos: gran, GRAN_PATH, ~/.config/gran e ~/.local/state/gran.
Zen: releases oficiais de zen-browser/desktop com SHA-256 verificado.
Yaru: fonte oficial ubuntu/yaru (compilar: $INSTALL_YARU).
Mise: Node LTS, Codex CLI e OpenCode.
Skills: gran, gran-app e gran-diagnose em ~/.agents/skills.
Shell padrão fish: $CHANGE_SHELL. Habilitar serviços de rede/Bluetooth: $ENABLE_SERVICES.
Aplicativos opcionais dos atalhos não são instalados.
Boot silencioso e Plymouth atual: $CONFIGURE_BOOT. SDDM: $CONFIGURE_LOGIN. Autologin: $AUTOLOGIN.
Energia do notebook: teclado 30s na bateria, tela 20min com carga <=25%, limite de carga 95%.
Kitty: cursor trail atual e fish; cores compartilhadas entre GTK/Qt/terminais e Zen.
Nenhum repositório, chave ou mirror adicional será configurado.

Pacotes oficiais explícitos (${#PACKAGES[@]}):
EOF
printf '  %s\n' "${PACKAGES[@]}"
if (( ${#NOTEBOOK_PACKAGES[@]} )); then printf 'Hardware detectado: %s\n' "${NOTEBOOK_PACKAGES[*]}"; fi
[[ $MODE == install ]] || { echo; echo 'Para instalar: bash install.sh --install'; exit 0; }
[[ $EUID -ne 0 ]] || die 'Execute como usuário comum, sem sudo no comando inicial.'
[[ -t 0 && -t 1 ]] || die 'O assistente precisa de um terminal interativo.'
[[ $(uname -m) == x86_64 && -f /etc/arch-release ]] || die 'O destino deve ser Arch Linux x86_64 instalado.'
command -v sudo >/dev/null || die 'Configure sudo antes de instalar.'
if pacman -Qq omarchy >/dev/null 2>&1 || pacman -Qq omarchy-dev >/dev/null 2>&1; then
  die 'Use um Arch enxuto ou VM; a máquina de origem não deve ser convertida.'
fi
if pacman-conf | grep -Eqi 'omarchy\.(org|cn)|^\[omarchy\]'; then
  die 'O destino contém configuração de repositório Omarchy. Prepare um Arch com fontes oficiais.'
fi
verify
read -r -p 'Aplicar o plano neste Arch? Digite INSTALAR: ' answer
[[ $answer == INSTALAR ]] || { echo 'Cancelado.'; exit 0; }
sudo -v
STAMP=$(date -u +%Y%m%dT%H%M%S)-$$
SYSTEM_BACKUP="/var/backups/gran/$STAMP"
USER_BACKUP="$HOME/.local/state/gran/install-backups/$STAMP"
mkdir -p "$USER_BACKUP"
sudo mkdir -p "$SYSTEM_BACKUP"
getent passwd "$USER" | sudo tee "$SYSTEM_BACKUP/passwd-entry.txt" >/dev/null
for relative in .config/mise/config.toml .config/mimeapps.list .local/share/applications/mimeapps.list; do
  if [[ -e $HOME/$relative ]]; then
    mkdir -p "$USER_BACKUP/$(dirname "$relative")"
    cp -a "$HOME/$relative" "$USER_BACKUP/$relative"
  fi
done
for service in NetworkManager.service bluetooth.service; do
  systemctl is-enabled "$service" 2>&1 | sudo tee -a "$SYSTEM_BACKUP/service-states.txt" >/dev/null || true
done

echo '[1/5] Atualizando e instalando pacotes oficiais do Arch...'
sudo pacman -Syu --needed "${PACKAGES[@]}" "${NOTEBOOK_PACKAGES[@]}"
for pair in 'hyprland 0.57.0' 'quickshell 0.3.2'; do
  read -r package minimum <<< "$pair"
  installed=$(pacman -Q "$package" | awk '{print $2}')
  [[ $(vercmp "$installed" "$minimum") -ge 0 ]] || die "$package precisa ser >= $minimum para esta configuração."
done

echo '[2/5] Aplicando o desktop, atalhos e skills Gran...'
python "$ROOT/scripts/apply-home.py" --home "$HOME"
export GRAN_PATH="$HOME/.local/share/gran"
export PATH="$HOME/.local/bin:$HOME/.local/share/mise/shims:$GRAN_PATH/bin:$PATH"
find "$GRAN_PATH/bin" "$HOME/.local/bin" -maxdepth 1 -type f -name 'gran*' -exec chmod +x {} +
chmod +x "$HOME/.local/bin/zen-browser"
for destination in /etc/profile.d/gran.sh /etc/pam.d/gran-lock-password; do
  if [[ -e $destination ]]; then sudo cp -a "$destination" "$SYSTEM_BACKUP/${destination##*/}"; fi
done
sudo install -Dm644 "$ROOT/snapshot/pam/gran-lock-password" /etc/pam.d/gran-lock-password
sudo install -Dm644 "$ROOT/overlay/.local/share/gran/profile.sh" /etc/profile.d/gran.sh
SYSTEM_OPTIONS=(--user "$USER" --home "$HOME" --execute)
[[ $CONFIGURE_BOOT == 1 ]] || SYSTEM_OPTIONS+=(--no-boot)
[[ $CONFIGURE_LOGIN == 1 ]] || SYSTEM_OPTIONS+=(--no-login)
[[ $AUTOLOGIN == 1 ]] || SYSTEM_OPTIONS+=(--no-autologin)
for path in /etc/systemd/system/display-manager.service /etc/systemd/system/default.target; do
  [[ ! -e $path ]] || sudo cp -a "$path" "$SYSTEM_BACKUP/${path##*/}"
done
sudo python "$ROOT/scripts/apply-system.py" "${SYSTEM_OPTIONS[@]}"

echo '[3/5] Instalando as ferramentas de terminal pelo mise...'
mise use -g node@lts
mise use -g npm:@openai/codex@latest npm:opencode-ai@latest
mise reshim

echo '[4/5] Instalando programas diretamente dos projetos upstream...'
gran app install zen
if [[ $INSTALL_YARU == 1 ]]; then gran app install yaru; fi
export XDG_CURRENT_DESKTOP=Hyprland
xdg-settings set default-web-browser zen.desktop
for type in x-scheme-handler/http x-scheme-handler/https text/html application/xhtml+xml; do
  xdg-mime default zen.desktop "$type"
done
python - "$ROOT/snapshot/appearance.json" "$USER_BACKUP/appearance.json" <<'PY'
import json, subprocess, sys
preferences = json.load(open(sys.argv[1]))
previous = {key: subprocess.check_output(
    ['gsettings', 'get', 'org.gnome.desktop.interface', key], text=True).strip()
    for key in preferences}
with open(sys.argv[2], 'w') as backup:
    json.dump(previous, backup, indent=2)
for key, value in preferences.items():
    subprocess.run(['gsettings', 'set', 'org.gnome.desktop.interface', key, value], check=True)
PY
xdg-user-dirs-update
fc-cache -f
gran theme sync

echo '[5/5] Configurando shell e serviços...'
if [[ $CHANGE_SHELL == 1 && $(getent passwd "$USER" | cut -d: -f7) != /usr/bin/fish ]]; then
  grep -qx /usr/bin/fish /etc/shells || die '/usr/bin/fish ausente em /etc/shells.'
  sudo chsh -s /usr/bin/fish "$USER"
fi
if [[ $ENABLE_SERVICES == 1 ]]; then sudo systemctl enable NetworkManager.service bluetooth.service; fi
sudo systemctl daemon-reload
sudo systemctl enable gran-charge-limit.service
for package in "${NOTEBOOK_PACKAGES[@]}"; do
  case "$package" in
    extra/asusctl) sudo systemctl enable asusd.service ;;
    extra/thermald) sudo systemctl enable thermald.service ;;
  esac
done
if [[ $CONFIGURE_LOGIN == 1 ]]; then
  sudo systemctl enable --force sddm.service
  sudo systemctl set-default graphical.target
fi
echo
echo 'Gran instalado. Reinicie quando desejar; o SDDM iniciará o desktop conforme o plano.'
echo 'Alternativa pelo TTY: gran session'
echo 'Valide no desktop com: gran doctor'
echo 'Atualize com: gran update'
echo 'Skills: gran skills list'
echo "Backups: $SYSTEM_BACKUP e $USER_BACKUP"
