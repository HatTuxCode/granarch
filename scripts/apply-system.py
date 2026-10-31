#!/usr/bin/env python3
"""Stage/apply notebook, login and boot appearance without copying disk identifiers."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BOOT_FLAGS = ('quiet', 'splash', 'loglevel=0', 'systemd.show_status=false',
              'rd.udev.log_level=0', 'vt.global_cursor_default=0',
              'initramfs_async=0', 'systemd.tty.term.console=dumb')
PLYMOUTH_DROPIN = '''# Preserve the target's storage/encryption hooks; add only the boot splash.
if [[ " ${HOOKS[*]} " != *" plymouth "* ]]; then
  _gran_hooks=()
  _gran_inserted=0
  for _gran_hook in "${HOOKS[@]}"; do
    _gran_hooks+=("$_gran_hook")
    if [[ $_gran_hook == systemd || $_gran_hook == udev ]] && (( !_gran_inserted )); then
      _gran_hooks+=(plymouth)
      _gran_inserted=1
    fi
  done
  (( _gran_inserted )) || { echo "Gran: no systemd/udev initramfs hook" >&2; return 1; }
  HOOKS=("${_gran_hooks[@]}")
  unset _gran_hooks _gran_inserted _gran_hook
fi
[[ ! -f /etc/vconsole.conf ]] || FILES+=(/etc/vconsole.conf)
'''


def commandline(value):
    for flag in BOOT_FLAGS:
        key = flag.split('=', 1)[0]
        pattern = r'(?<!\S)' + re.escape(key) + (r'=\S+' if '=' in flag else r'(?!\S)')
        value = re.sub(pattern, '', value)
    return value.strip() + ' ' + ' '.join(BOOT_FLAGS)


def boot_files(root):
    for relative in ('boot/limine.conf', 'efi/limine.conf', 'boot/efi/limine.conf', 'boot/limine/limine.conf'):
        path = root / relative
        if path.is_file():
            return 'limine', [path]
    for relative in ('boot/loader/loader.conf', 'efi/loader/loader.conf', 'boot/efi/loader/loader.conf'):
        path = root / relative
        if path.is_file() or (path.parent / 'entries').is_dir() or (path.parent.parent / 'EFI/systemd/systemd-bootx64.efi').is_file():
            return 'systemd-boot', [path, *sorted((path.parent / 'entries').glob('*.conf'))]
    if (root / 'etc/default/grub').is_file() and (root / 'boot/grub/grub.cfg').is_file():
        return 'grub', [root / 'etc/default/grub']
    raise RuntimeError('Nenhuma configuração Limine, systemd-boot ou GRUB encontrada. Instale o bootloader primeiro.')


def apply(root, user, home, boot=True, login=True, autologin=True, execute=False):
    if not re.fullmatch(r'[a-z_][a-z0-9_-]*\$?', user):
        raise ValueError('Invalid target username')
    if not home.is_absolute() or any(char in str(home) for char in ('\n', '\r', '"')):
        raise ValueError('Invalid target home')
    root = root.resolve()
    if execute and (root != Path('/') or os.geteuid() != 0):
        raise RuntimeError('--execute requires root on the actual target system')
    loader, loader_files = boot_files(root) if boot else (None, [])
    if boot and not list((root / 'etc/mkinitcpio.d').glob('*.preset')):
        raise RuntimeError('Nenhum preset mkinitcpio encontrado; configure a geração do initramfs no Arch básico.')
    backup = root / 'var/backups/gran' / ('system-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'))
    for ancestor in backup.parents:
        if ancestor == root:
            break
        if ancestor.is_symlink():
            raise RuntimeError(f'Symlink parent requires manual review: {ancestor}')
    backup.mkdir(parents=True)
    changed = []
    def write(relative, payload, mode=0o644):
        destination = root / relative
        for ancestor in destination.parents:
            if ancestor == root:
                break
            if ancestor.is_symlink():
                raise RuntimeError(f'Symlink parent requires manual review: {ancestor}')
        if destination.exists() or destination.is_symlink():
            previous = backup / relative
            previous.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(destination, previous, follow_symlinks=False)
            destination.unlink()
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(payload)
        destination.chmod(mode)
        changed.append(relative)
        (backup / 'changes.json').write_text(json.dumps(changed, indent=2) + '\n')
    policy = json.loads((ROOT / 'manifests/notebook.json').read_text())
    vendor_file = root / 'sys/class/dmi/id/sys_vendor'
    vendor = vendor_file.read_text().lower() if vendor_file.exists() else ''
    is_asus = 'asus' in vendor
    for source in sorted((ROOT / 'snapshot/system').rglob('*')):
        if not source.is_file():
            continue
        relative = str(source.relative_to(ROOT / 'snapshot/system'))
        if 'plymouth/' in relative and not boot:
            continue
        if 'sddm/' in relative and not login:
            continue
        if relative.startswith('etc/asusd/') and not is_asus:
            continue
        write(relative, source.read_bytes(), source.stat().st_mode & 0o777)
    write('etc/systemd/logind.conf.d/90-gran-power.conf',
          b'[Login]\nHandlePowerKey=ignore\nInhibitDelayMaxSec=15\n')
    if is_asus:
        state = policy['asus_fnlock_default']
        if state not in ('Y', 'N'):
            raise ValueError('Invalid ASUS Fn Lock policy')
        write('etc/modprobe.d/gran-asus-wmi.conf', f'options asus_wmi fnlock_default={state}\n'.encode())
    limit = policy['charge_limit_percent']
    if not isinstance(limit, int) or not 1 <= limit <= 100:
        raise ValueError('Invalid charge threshold')
    charge = f'''#!/usr/bin/env bash
for file in /sys/class/power_supply/BAT*/charge_control_end_threshold; do
  [[ ! -w $file ]] || printf '%s\\n' {limit} > "$file"
done
'''
    write('usr/local/libexec/gran-charge-limit', charge.encode(), 0o755)
    write('etc/udev/rules.d/90-gran-battery-limit.rules',
          b'SUBSYSTEM=="power_supply", ACTION=="add|change", RUN+="/usr/local/libexec/gran-charge-limit"\n')
    write('etc/systemd/system/gran-charge-limit.service', b'''[Unit]
Description=Restore the Gran notebook battery charge limit
After=systemd-udev-settle.service
[Service]
Type=oneshot
ExecStart=/usr/local/libexec/gran-charge-limit
[Install]
WantedBy=multi-user.target
''')
    if login:
        # Reproduce the current SDDM flow. Relogin=false keeps an explicit logout at the greeter.
        config = '[General]\nDisplayServer=wayland\n[Wayland]\nCompositorCommand=start-hyprland -- --config /usr/share/sddm/gran-hyprland.lua\n[Theme]\nCurrent=gran\n[Users]\nRememberLastUser=true\nRememberLastSession=true\n'
        if autologin:
            config += f'[Autologin]\nUser={user}\nSession=gran.desktop\nRelogin=false\n'
        write('etc/sddm.conf.d/90-gran.conf', config.encode())
        write('usr/share/wayland-sessions/gran.desktop', b'''[Desktop Entry]
Name=Gran (Hyprland uwsm)
Comment=GranArch desktop
Exec=/usr/local/bin/gran-session
TryExec=/usr/bin/uwsm
Type=Application
DesktopNames=Hyprland
''')
        write('usr/local/bin/gran-session', b'''#!/usr/bin/env bash
export GRAN_PATH="$HOME/.local/share/gran"
export PATH="$HOME/.local/bin:$HOME/.local/share/mise/shims:$GRAN_PATH/bin:$PATH"
exec "$GRAN_PATH/bin/gran-session"
''', 0o755)
    if boot:
        write('etc/plymouth/plymouthd.conf', b'[Daemon]\nTheme=gran\n')
        write('etc/mkinitcpio.conf.d/90-gran-plymouth.conf', PLYMOUTH_DROPIN.encode())
        for path in loader_files:
            relative = str(path.relative_to(root))
            value = path.read_text() if path.exists() else ''
            if loader == 'limine':
                if re.search(r'(?im)^\s*timeout\s*:', value):
                    value = re.sub(r'(?im)^\s*timeout\s*:.*$', 'timeout: 0', value)
                else:
                    value = 'timeout: 0\n' + value
                value = re.sub(r'(?im)^([ \t]*(?:kernel_)?cmdline\s*:\s*)(.*)$',
                               lambda match: match[1] + commandline(match[2]), value)
            elif loader == 'systemd-boot':
                if path.name == 'loader.conf':
                    value = re.sub(r'(?m)^timeout\s+.*$', '', value).rstrip() + '\ntimeout 0\n'
                else:
                    value = re.sub(r'(?m)^(options[ \t]+)(.*)$',
                                   lambda match: match[1] + commandline(match[2]), value)
            else:
                value = re.sub(r'(?m)^GRUB_TIMEOUT=.*$', '', value)
                value = re.sub(r'(?m)^GRUB_TIMEOUT_STYLE=.*$', '', value)
                match = re.search(r'(?m)^GRUB_CMDLINE_LINUX_DEFAULT=(.*)$', value)
                parts = shlex.split(match[1], comments=True) if match else []
                if len(parts) > 1 or any(token in ''.join(parts) for token in ('$', '`', '\n', '\r')):
                    raise RuntimeError('GRUB_CMDLINE_LINUX_DEFAULT dinâmico precisa de revisão manual.')
                existing = parts[0] if parts else ''
                value = re.sub(r'(?m)^GRUB_CMDLINE_LINUX_DEFAULT=.*$', '', value)
                value = value.rstrip() + '\nGRUB_TIMEOUT=0\nGRUB_TIMEOUT_STYLE=hidden\n'
                value += 'GRUB_CMDLINE_LINUX_DEFAULT=' + shlex.quote(commandline(existing)) + '\n'
            write(relative, value.encode())
        target_cmdline = root / 'etc/kernel/cmdline'
        if target_cmdline.exists():
            write('etc/kernel/cmdline', (commandline(target_cmdline.read_text().strip()) + '\n').encode())
        elif (root / 'proc/cmdline').is_file():
            # Read only the destination's running command line, never the export machine's.
            value = (root / 'proc/cmdline').read_text().strip()
            value = re.sub(r'(?<!\S)(?:BOOT_IMAGE|initrd)=\S+\s*', '', value)
            write('etc/kernel/cmdline', (commandline(value) + '\n').encode())
    result = {'bootloader': loader, 'system_files': len(changed), 'backup': str(backup),
              'asus_policy_applied': is_asus, 'autologin': login and autologin}
    if execute:
        if boot:
            subprocess.run(['mkinitcpio', '-P'], check=True)
            if loader == 'grub':
                subprocess.run(['grub-mkconfig', '-o', '/boot/grub/grub.cfg'], check=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('/'))
    parser.add_argument('--user', required=True)
    parser.add_argument('--home', type=Path, required=True)
    parser.add_argument('--no-boot', action='store_true')
    parser.add_argument('--no-login', action='store_true')
    parser.add_argument('--no-autologin', action='store_true')
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    print(json.dumps(apply(args.root, args.user, args.home, not args.no_boot,
                           not args.no_login, not args.no_autologin, args.execute), indent=2))


if __name__ == '__main__':
    main()
