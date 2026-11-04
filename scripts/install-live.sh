#!/usr/bin/env bash
# Run only inside the official Arch live ISO, on deliberately mounted partitions.
set -euo pipefail
[[ $# == 3 ]] || { echo 'Uso: ./install.sh --live /mnt USER HOST' >&2; exit 2; }
target=$1; user=$2; hostname=$3
[[ $EUID == 0 && -d /run/archiso && -d /sys/firmware/efi ]] || { echo 'Requer ISO oficial Arch x86_64 iniciada em UEFI, como root.' >&2; exit 1; }
[[ $(uname -m) == x86_64 && $target == /mnt ]] || { echo 'Destino suportado: /mnt, arquitetura x86_64.' >&2; exit 1; }
[[ $user =~ ^[a-z_][a-z0-9_-]{0,30}$ && $user != root ]] || { echo 'Nome de usuário inválido.' >&2; exit 2; }
[[ $hostname =~ ^[a-zA-Z0-9][a-zA-Z0-9-]{0,62}$ ]] || { echo 'Hostname inválido.' >&2; exit 2; }
mountpoint -q /mnt
mountpoint -q /mnt/boot
[[ $(findmnt -nro FSTYPE -M /mnt) == ext4 && $(findmnt -nro FSTYPE -M /mnt/boot) == vfat ]] || { echo 'Requer raiz ext4 em /mnt e ESP FAT32 em /mnt/boot.' >&2; exit 1; }
[[ ! -e /mnt/etc/os-release && ! -e /mnt/boot/EFI && ! -e /mnt/boot/loader ]] || { echo 'Destino já tem sistema/bootloader; use partições novas e vazias.' >&2; exit 1; }
[[ -z $(find /mnt -mindepth 1 -maxdepth 1 ! -name lost+found ! -name boot -print -quit) ]] || { echo 'Raiz não está vazia.' >&2; exit 1; }
project=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
[[ $project != /mnt/* ]] || { echo 'Mantenha o projeto fora de /mnt.' >&2; exit 1; }
source_device=$(findmnt -nro SOURCE -M /mnt)
[[ -b $source_device ]] || { echo 'Raiz precisa ser dispositivo de bloco.' >&2; exit 1; }
# Support both plain ext4 and an already-open LUKS root. No source-machine UUIDs.
root_options="root=UUID=$(blkid -s UUID -o value "$source_device") rw"
if [[ $(lsblk -dnro TYPE "$source_device") == crypt ]]; then
 parent=$(lsblk -dnro PKNAME "$source_device")
 [[ -n $parent && $(blkid -s TYPE -o value "/dev/$parent") == crypto_LUKS ]] || { echo 'Mapeamento LUKS não reconhecido.' >&2; exit 1; }
 root_options="rd.luks.name=$(blkid -s UUID -o value "/dev/$parent")=cryptroot root=/dev/mapper/cryptroot rw"
fi
printf 'Destino: %s\nRaiz: %s\nESP: %s\nUsuário: %s\nHost: %s\n' "$target" "$source_device" "$(findmnt -nro SOURCE -M /mnt/boot)" "$user" "$hostname"
read -r -p 'Digite INSTALAR para gravar o sistema nas partições montadas: ' answer
[[ $answer == INSTALAR ]] || exit 1
mapfile -t packages < <(sed '/^[[:space:]]*#/d;/^[[:space:]]*$/d' "$project/manifests/packages.txt")
pacstrap -K /mnt "${packages[@]}" sudo dosfstools e2fsprogs cryptsetup
# Single write: repeating genfstab must not accumulate duplicate entries.
genfstab -U /mnt > /mnt/etc/fstab
printf '%s\n' "$hostname" > /mnt/etc/hostname
printf '127.0.0.1 localhost\n::1 localhost\n127.0.1.1 %s.localdomain %s\n' "$hostname" "$hostname" > /mnt/etc/hosts
arch-chroot /mnt useradd -m -G wheel -s /usr/bin/fish "$user"
echo 'Defina a senha do usuário (também desbloqueia o cofre no login):'
arch-chroot /mnt passwd "$user"
echo 'Defina a senha de recuperação do root:'
arch-chroot /mnt passwd root
# systemd initramfs supports both normal and encrypted root with Portuguese input.
cat > /mnt/etc/mkinitcpio.conf <<'MKINIT'
MODULES=(vmd nvme i915)
BINARIES=()
FILES=()
HOOKS=(base systemd autodetect microcode modconf kms keyboard sd-vconsole block sd-encrypt filesystems fsck)
MKINIT
arch-chroot /mnt bootctl --esp-path=/boot install
mkdir -p /mnt/boot/loader/entries
printf 'default granarch.conf\ntimeout 3\neditor no\n' > /mnt/boot/loader/loader.conf
printf 'title Arch Linux — GranArch\nlinux /vmlinuz-linux\ninitrd /initramfs-linux.img\noptions %s\n' "$root_options" > /mnt/boot/loader/entries/granarch.conf
stage="/home/$user/.cache/granarch-installer"
mkdir -p "/mnt$stage"
# Exclude Git metadata and environment-provided agent mounts.
tar -C "$project" --exclude=.git --exclude=.agents --exclude=.codex --exclude=.aws --exclude=dist -cf - . | tar -C "/mnt$stage" -xf -
arch-chroot /mnt python3 "$stage/scripts/check-versions.py"
arch-chroot /mnt python3 "$stage/scripts/configure-system.py" "$user"
arch-chroot /mnt mkinitcpio -P
arch-chroot /mnt chown -R "$user:$user" "$stage"
arch-chroot /mnt runuser -u "$user" -- env -u DBUS_SESSION_BUS_ADDRESS -u HYPRLAND_INSTANCE_SIGNATURE HOME="/home/$user" USER="$user" bash "$stage/scripts/user-install.sh"
printf 'Concluído. Desmonte com umount -R /mnt e reinicie. Selecione GranArch no SDDM.\n'
