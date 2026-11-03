#!/usr/bin/env bash
# Repair the command and update the affected Gran runtime files, preserving backups.
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
[[ $EUID -ne 0 ]] || { echo 'Execute como usuário comum.' >&2; exit 1; }
python - "$ROOT" <<'PY'
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import sys

root, home = Path(sys.argv[1]), Path.home()
backup = home / '.local/state/gran/opencode-backups' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
files = {
    '.local/share/gran/bin/gran-opencode-install': 'overlay/.local/share/gran/bin/gran-opencode-install',
    '.local/share/gran/bin/gran-update': 'overlay/.local/share/gran/bin/gran-update',
    '.local/share/gran/bin/gran-doctor': 'overlay/.local/share/gran/bin/gran-doctor',
    '.local/share/gran/lib/control.py': 'overlay/.local/share/gran/lib/control.py',
    '.local/share/gran/optional-apps.json': 'manifests/optional-apps.json',
    '.local/share/gran/sources.json': 'manifests/sources.json',
}
installed = (home / '.local/share/gran/version').is_file()
targets = list(files) if installed else []
targets.append('.config/mise/config.toml')
for parent in (backup, *backup.parents):
    if parent == home:
        break
    if parent.is_symlink():
        raise SystemExit(f'Symlink requires manual review: {parent}')
for relative in targets:
    target = home / relative
    for parent in (target, *target.parents):
        if parent == home:
            break
        if parent.is_symlink():
            raise SystemExit(f'Symlink requires manual review: {parent}')
    if target.exists():
        saved = backup / relative
        saved.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, saved)
subprocess.run(['bash', str(root / 'overlay/.local/share/gran/bin/gran-opencode-install')], check=True)
if installed:
    backup.mkdir(parents=True, exist_ok=True)
    (backup / 'changes.json').write_text(json.dumps(list(files), indent=2) + '\n')
    for relative, source in files.items():
        target = home / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / source, target)
print('OpenCode reparado. Backups dos arquivos existentes:', backup)
PY
