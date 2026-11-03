#!/usr/bin/env bash
# Sourced by install.sh; read-only checks against the destination's sync databases.
gran_select_boot() {
  if [[ $CONFIGURE_BOOT == auto ]]; then
    CONFIGURE_BOOT=1
    case "$DISTRO" in cachyos|endeavouros) CONFIGURE_BOOT=0 ;; esac
  fi
}

gran_filter_boot_packages() {
  if [[ $CONFIGURE_BOOT == 0 ]]; then
    local package
    local -a filtered=()
    for package in "${PACKAGES[@]}"; do
      case "${package#*/}" in mkinitcpio|plymouth) ;; *) filtered+=("$package") ;; esac
    done
    PACKAGES=("${filtered[@]}")
  fi
}

gran_preflight() {
  local executable package info version minimum
  [[ $(uname -m) == x86_64 && -f /etc/arch-release ]] || die 'Use Arch Linux, EndeavourOS ou CachyOS x86_64 já instalado.'
  [[ ! -d /run/archiso && ! -d /run/miso && ! -d /run/cachyos ]] || die 'Reinicie no sistema instalado; não execute na ISO live.'
  for executable in sudo pacman pacman-conf vercmp getent systemctl sha256sum tar tee; do
    command -v "$executable" >/dev/null || die "Pré-requisito ausente: $executable"
  done
  [[ -w $HOME && -d $HOME ]] || die 'A pasta HOME precisa existir e permitir escrita.'
  if pacman-conf | grep -Eqi 'omarchy\.(org|cn)|^\[omarchy\]'; then
    die 'Use uma instalação mínima separada, sem repositório Omarchy.'
  fi
  for package in "${PACKAGES[@]}" "${NOTEBOOK_PACKAGES[@]}"; do
    pacman -Si "$package" >/dev/null || die "Pacote indisponível: $package. Confira internet/repositórios e execute sudo pacman -Syu antes de tentar novamente."
  done
  for info in 'hyprland 0.57.0' 'quickshell 0.3.2'; do
    read -r package minimum <<< "$info"
    [[ $DISTRO == cachyos ]] || package="extra/$package"
    version=$(LC_ALL=C pacman -Si "$package" | awk '/^Version[[:space:]]*:/ {print $3; exit}')
    [[ -n $version ]] || die "Não consegui consultar a versão de $package."
    [[ $(vercmp "$version" "$minimum") -ge 0 ]] || die "$package disponível ($version) precisa ser >= $minimum. Atualize com sudo pacman -Syu; a configuração usa a API Lua do Hyprland."
  done
  if [[ $CONFIGURE_BOOT == 1 ]]; then
    if [[ $DISTRO == endeavouros ]]; then
      die 'No EndeavourOS, preserve dracut e kernel-install com --no-boot; a personalização de boot do Gran exige o fluxo mkinitcpio do Arch.'
    fi
    # Validate prerequisites before touching packages or the user's desktop.
    local recognized=0 path
    for path in /boot/limine.conf /efi/limine.conf /boot/efi/limine.conf /boot/limine/limine.conf \
                /boot/loader/loader.conf /efi/loader/loader.conf /boot/efi/loader/loader.conf \
                /boot/loader/entries /efi/loader/entries /boot/efi/loader/entries; do
      [[ ! -e $path ]] || recognized=1
    done
    if [[ -f /etc/default/grub && -f /boot/grub/grub.cfg ]]; then recognized=1; fi
    [[ $recognized == 1 ]] || die 'Bootloader não reconhecido. Use --no-boot para preservar o boot do destino.'
    compgen -G '/etc/mkinitcpio.d/*.preset' >/dev/null || die 'Sem presets mkinitcpio. Use --no-boot para preservar o gerador do destino.'
    [[ ! -f /etc/default/limine && ! -f /etc/sdboot-manage.conf ]] || die 'Boot gerenciado pela distribuição. Use --no-boot para preservá-lo.'
  fi
  echo 'OK: plataforma, pacotes disponíveis e versões mínimas.'
}

gran_check_tools() {
  local executable
  for executable in python dbus-run-session gsettings glib-compile-schemas update-desktop-database \
                    mise git curl xdg-settings xdg-mime xdg-user-dirs-update fc-cache; do
    command -v "$executable" >/dev/null || die "Dependência não disponível após pacman: $executable"
  done
  if [[ $INSTALL_YARU == 1 ]]; then
    for executable in meson ninja sassc xcursorgen inkscape xvfb-run xauth; do
      command -v "$executable" >/dev/null || die "Dependência Yaru ausente: $executable"
    done
  fi
}
