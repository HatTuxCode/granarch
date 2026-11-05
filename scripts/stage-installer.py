#!/usr/bin/env python3
import os,shutil
from pathlib import Path
source=Path(__file__).resolve().parents[1]
target=Path('/opt/granarch-installer')
if os.geteuid()!=0:raise SystemExit('Requer root no destino Arch.')
if source.resolve()!=target.resolve():
    shutil.copytree(source,target,dirs_exist_ok=True,ignore=shutil.ignore_patterns('.git','.agents','.codex','.aws','dist','__pycache__','*.pyc','src','pkg','*.pkg.tar.*'))
    for path in [target,*target.rglob('*')]:
        if not path.is_symlink():os.chown(path,0,0)
