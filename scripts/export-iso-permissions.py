#!/usr/bin/env python3
"""Preserve repository executables when archiso normalizes airootfs file modes."""
import argparse, shlex
from pathlib import Path

def export(root):
    lines=[]
    for path in sorted(root.rglob('*')):
        if path.is_file() and not path.is_symlink() and path.stat().st_mode & 0o111:
            name='/'+path.relative_to(root).as_posix()
            lines.append('file_permissions['+shlex.quote(name)+']='+'"0:0:755"')
    return '\n'.join(lines)+'\n'
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('airootfs',type=Path)
    print(export(parser.parse_args().airootfs),end='')
