#!/usr/bin/env python3
"""Update only Gran branding, browser integration and Files appearance."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    '.config/fastfetch/config.jsonc', '.config/gran/branding/about.txt',
    '.config/gtk-4.0/gran-nautilus-blur.css', '.config/gran/scripts/sync-nautilus-zen.py',
    '.local/share/gran/logo.txt', '.local/share/gran/icon.txt',
    '.local/share/gran/shell/plugins/menu/BarWidget.qml',
    '.local/share/gran/bin/gran-launch-about', '.local/share/gran/bin/gran-show-logo',
    '.local/share/gran/bin/gran-app', '.local/share/gran/bin/gran-theme-sync',
    '.local/share/gran/default/zen/reference.json', '.local/bin/zen-browser',
    '.local/share/applications/org.gnome.Nautilus.desktop',
)
# Deploy the complete native bar together with its matching model/widgets.
FILES += tuple(str(path.relative_to(ROOT / 'overlay')) for path in sorted(
    (ROOT / 'overlay/.local/share/gran/shell/plugins/bar').rglob('*')) if path.is_file())


def apply(home):
    home = home.resolve()
    if not (home / '.local/share/gran/version').is_file():
        raise RuntimeError('Instale o GranArch antes de aplicar esta atualização.')
    backup = home / '.local/state/gran/appearance-backups' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    destinations = [home / relative for relative in FILES]
    destinations += [backup, home / '.local/share/applications/zen.desktop', home / '.config/gran/shell.json']
    for destination in destinations:
        for parent in (destination, *destination.parents):
            if parent == home:
                break
            if parent.is_symlink():
                raise RuntimeError(f'Symlink requires manual review: {parent}')
    backup.mkdir(parents=True)
    changes = []
    for relative in FILES:
        source, target = ROOT / 'overlay' / relative, home / relative
        if target.is_file() and target.read_bytes() == source.read_bytes():
            continue
        if target.exists():
            saved = backup / relative
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, saved)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        changes.append(relative)
        (backup / 'changes.json').write_text(json.dumps(changes, indent=2) + '\n')
    shell_path = home / '.config/gran/shell.json'
    shell = json.loads(shell_path.read_text())
    if shell.get('bar', {}).get('id') == 'hattux.bar':
        saved = backup / '.config/gran/shell.json'
        saved.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(shell_path, saved)
        shell['bar']['id'] = 'gran.bar'
        shell_path.write_text(json.dumps(shell, indent=2) + '\n')
        changes.append('.config/gran/shell.json')
        (backup / 'changes.json').write_text(json.dumps(changes, indent=2) + '\n')
    desktop = home / '.local/share/applications/zen.desktop'
    if desktop.exists():
        saved = backup / '.local/share/applications/zen.desktop'
        saved.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(desktop, saved)
    env = dict(os.environ, HOME=str(home), GRAN_PATH=str(home / '.local/share/gran'))
    env['PATH'] = str(home / '.local/bin') + ':' + str(home / '.local/share/gran/bin') + ':' + env.get('PATH', '')
    subprocess.run([sys.executable, str(home / '.local/share/gran/bin/gran-theme-sync')], env=env, check=True)
    # Repair the existing browser's icons/launcher without downloading or downgrading it.
    subprocess.run([sys.executable, str(home / '.local/share/gran/bin/gran-app'), 'repair', 'zen'], env=env, check=True)
    print(f'Aparência atualizada. Backup: {backup}')
    print('Feche e reabra Zen e Files. Saia e entre na sessão para recarregar a barra.')
    return backup


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', required=True, type=Path)
    apply(parser.parse_args().home)
