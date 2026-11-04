#!/usr/bin/env python3
"""Apply the allowlisted desktop to a home, backing up every replaced file."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]
def apply(home):
    home=home.resolve(); backup=home/'.local/state/gran/backups'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    for src in sorted((ROOT/'payload/home').rglob('*')):
        if src.is_symlink(): raise ValueError(f'Link inesperado no payload: {src}')
        if not src.is_file(): continue
        relative=src.relative_to(ROOT/'payload/home'); dst=home/relative
        # Never traverse symlinks into another profile or outside the destination.
        if dst.is_symlink() or any(p.is_symlink() for p in dst.parents if p!=home.parent):
            raise ValueError(f'Destino contém link simbólico: {dst}')
        data=src.read_bytes()
        try: data=data.decode().replace('@HOME@',str(home)).encode()
        except UnicodeError: pass
        if dst.exists():
            if dst.read_bytes()==data: continue
            saved=backup/relative; saved.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(dst,saved)
        dst.parent.mkdir(parents=True,exist_ok=True); dst.write_bytes(data); dst.chmod(src.stat().st_mode&0o777)
    # Overrides supersede config.toml; archive them before applying the requested profile.
    settings=home/'.local/state/noctalia/settings.toml'
    if settings.exists():
        saved=backup/'.local/state/noctalia/settings.toml'; saved.parent.mkdir(parents=True,exist_ok=True)
        shutil.move(settings,saved)
    (home/'Work').mkdir(exist_ok=True)
    return backup
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--home',type=Path,default=Path.home());args=parser.parse_args()
    print('Backup:',apply(args.home))
