#!/usr/bin/env python3
"""Install the reference desktop's shortcuts, fish aliases and btop presentation."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def apply(home):
    home = home.resolve()
    if not (home / '.local/share/gran/version').is_file():
        raise RuntimeError('Instale o GranArch antes de atualizar os atalhos.')
    manifest = json.loads((ROOT / 'manifests/shortcuts.json').read_text())
    files = manifest['files'] + ['.config/fish/conf.d/10-gran.fish']
    backup = home / '.local/state/gran/shortcut-backups' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    for destination in [backup, *(home / relative for relative in files)]:
        for parent in (destination, *destination.parents):
            if parent == home:
                break
            if parent.is_symlink():
                raise RuntimeError(f'Symlink requires manual review: {parent}')
    changes = []
    for relative in files:
        source, destination = ROOT / 'overlay' / relative, home / relative
        payload = source.read_text().replace('@@GRAN_HOME@@', str(home)).encode()
        if destination.is_file() and destination.read_bytes() == payload:
            continue
        backup.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            saved = backup / relative
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(destination, saved)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(payload)
        destination.chmod(source.stat().st_mode & 0o777)
        changes.append(relative)
        (backup / 'changes.json').write_text(json.dumps(changes, indent=2) + '\n')
    print(f'Atalhos, aliases fish e btop atualizados: {len(changes)} arquivo(s). Backup: {backup if changes else "sem alterações"}')
    print('Abra um terminal novo para lt/lta. Saia e entre na sessão para recarregar os atalhos.')
    return backup if changes else None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', required=True, type=Path)
    apply(parser.parse_args().home)
