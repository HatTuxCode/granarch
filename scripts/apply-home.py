#!/usr/bin/env python3
"""Apply the Gran desktop, preserving every inherited binding and backing up existing files."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def apply(home):
    home = home.resolve()
    if home == Path('/'):
        raise ValueError('home cannot be /')
    home.mkdir(parents=True, exist_ok=True)
    backup = home / '.local/state/gran/backups' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    def validate_parent(destination):
        for ancestor in destination.parents:
            if ancestor == home:
                break
            if ancestor.is_symlink():
                raise RuntimeError(f'Symlink parent requires manual review: {ancestor}')
    validate_parent(backup)
    backup.mkdir(parents=True)
    changes = []
    recorded = set()

    def write(relative, payload, mode=0o644, link=None):
        destination = home / relative
        validate_parent(destination)
        previous = backup / relative
        if destination.exists() or destination.is_symlink():
            if destination.is_dir() and not destination.is_symlink():
                raise RuntimeError(f'Expected file: {destination}')
            if relative not in recorded:
                previous.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(destination, previous, follow_symlinks=False)
            destination.unlink()
        destination.parent.mkdir(parents=True, exist_ok=True)
        if link is None:
            destination.write_bytes(payload)
            destination.chmod(mode)
        else:
            destination.symlink_to(link)
        if relative not in recorded:
            recorded.add(relative)
            changes.append(relative)
            (backup / 'changes.json').write_text(json.dumps(changes, indent=2) + '\n')

    def tree(source, prefix=''):
        for path in sorted(source.rglob('*')):
            if not path.is_file():
                continue
            payload = path.read_bytes()
            try:
                payload = payload.decode().replace('@@GRAN_HOME@@', str(home)).encode()
            except UnicodeError:
                pass
            write(str(Path(prefix) / path.relative_to(source)), payload, path.stat().st_mode & 0o777)

    tree(ROOT / 'snapshot/runtime', '.local/share/gran')
    tree(ROOT / 'snapshot/home')
    tree(ROOT / 'overlay')
    tree(ROOT / 'skills', '.agents/skills')
    write('.local/share/gran/LICENSE', (ROOT / 'licenses/omarchy-MIT.txt').read_bytes())
    write('.local/share/gran/sources.json', (ROOT / 'manifests/sources.json').read_bytes())
    write('.local/share/gran/optional-apps.json', (ROOT / 'manifests/optional-apps.json').read_bytes())
    write('.config/gran/notebook.json', (ROOT / 'manifests/notebook.json').read_bytes())
    runtime = home / '.local/share/gran'
    env = runtime / 'default/hypr/envs.lua'
    value = env.read_text().replace('table.insert(kept, 1, bin_dir)',
        'table.insert(kept, 1, bin_dir)\ntable.insert(kept, 1, paths.home .. "/.local/bin")')
    write('.local/share/gran/default/hypr/envs.lua', value.encode())
    cli = runtime / 'bin/gran'
    value = cli.read_text().replace('gran debug               Print debugging information',
                                    'gran doctor              Check desktop configuration').replace(
                                        'Version and channel information', 'Installed Gran version')
    import re
    groups = {p.name.removeprefix('gran-').split('-')[0] for p in (runtime / 'bin').glob('gran-*')}
    value = '\n'.join(line for line in value.splitlines()
                      if not (match := re.match(r'GROUP_DESCRIPTIONS\[([^]]+)\]', line))
                      or match[1] in groups) + '\n'
    value = value.replace('join_words() {',
        'GROUP_DESCRIPTIONS[app]="Upstream applications"\n'
        'GROUP_DESCRIPTIONS[doctor]="Desktop health checks"\n'
        'GROUP_DESCRIPTIONS[skills]="Agent skills"\n'
        'GROUP_DESCRIPTIONS[session]="Desktop session"\n\njoin_words() {')
    write('.local/share/gran/bin/gran', value.encode(), 0o755)
    locale_generator = runtime / 'bin/gran-locale-generate'
    value = locale_generator.read_text().replace('registry=/usr/share/gran/default/i18n/locales.json',
        'registry="$(dirname -- "$(dirname -- "$(readlink -f -- "$0")")")/default/i18n/locales.json"')
    write('.local/share/gran/bin/gran-locale-generate', value.encode(), 0o755)
    remove_entry = runtime / 'bin/gran-remove-launcher-entry'
    value = remove_entry.read_text().replace('exec_line="$(sed',
        'if [[ $desktop_name == gran-webapp-* ]]; then\n'
        '  exec gran-webapp remove "${desktop_name#gran-webapp-}" --yes\n'
        'fi\n\nexec_line="$(sed')
    write('.local/share/gran/bin/gran-remove-launcher-entry', value.encode(), 0o755)
    # Optional titlebars are provided by the official Hyprland plugin, never a distro fork.
    modes = runtime / 'default/hypr/workspace-modes.lua'
    value = modes.read_text().replace('"/usr/lib/gran-hyprland-titlebars/titlebars.so"',
        '(os.getenv("HOME") or "") .. "/.local/share/hyprpm/hyprland-plugins/hyprbars.so"')
    write('.local/share/gran/default/hypr/workspace-modes.lua', value.encode())
    speed = runtime / 'shell/plugins/panels/speedtest/Panel.qml'
    write('.local/share/gran/shell/plugins/panels/speedtest/Panel.qml',
          speed.read_text().replace('speed.gran.org', 'speed.cloudflare.com').encode())
    battery = home / '.config/gran/plugins/hattux.battery-idle-dpms/Service.qml'
    value = battery.read_text().replace('Number(UPower.displayDevice.percentage)',
                                       'Number(UPower.displayDevice.percentage) * 100')
    write('.config/gran/plugins/hattux.battery-idle-dpms/Service.qml', value.encode())
    # User wrapper delegates to the actual Gran brightness helper, never to /usr/share/omarchy.
    script = home / '.local/bin/gran-brightness-keyboard'
    value = script.read_text().replace(
        'SYSTEM_BIN="/usr/share/gran/bin/gran-brightness-keyboard"',
        'SYSTEM_BIN="' + str(runtime / 'bin/gran-brightness-keyboard') + '"')
    write('.local/bin/gran-brightness-keyboard', value.encode(), 0o755)
    # The source's default input layout reads /etc; preserve the source machine's ABNT2 choice.
    write('.config/gran/keyboard-layouts',
          b'XKBLAYOUT=br\nXKBMODEL=abnt2\nXKBVARIANT=\nXKBOPTIONS=shift:both_capslock_cancel\n')
    # No inherited keybinding module is edited here: optional app bindings remain intact.
    kitty = (ROOT / 'snapshot/kitty-defaults.conf').read_text()
    kitty += '\n' + (home / '.config/kitty/kitty.conf').read_text()
    write('.config/kitty/kitty.conf', kitty.encode())
    autostart = home / '.config/hypr/autostart.lua'
    value = autostart.read_text() + '\n' + '''hl.env("QT_QPA_PLATFORMTHEME", "gtk3")
hl.env("QT_STYLE_OVERRIDE", "Fusion")
hl.env("QT_QUICK_CONTROLS_STYLE", "Fusion")
'''
    write('.config/hypr/autostart.lua', value.encode())
    write('.config/xdg-terminals.list', b'kitty.desktop\n')
    write('.config/gran/defaults/agent', b'codex\n')
    write('.local/state/gran/defaults/editor', b'nano\n')
    write('.local/state/gran/current/background', b'',
          link=home / '.local/share/gran/wallpaper.jpg')
    print(f'Applied {len(changes)} files. Backups: {backup}')
    return backup


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', type=Path, required=True)
    apply(parser.parse_args().home)


if __name__ == '__main__':
    main()
