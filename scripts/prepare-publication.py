#!/usr/bin/env python3
"""Copy an explicit project allowlist into a Git publication worktree."""
import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
INCLUDE = ('README.md', '.gitignore', 'install.sh', 'docs', 'manifests', 'scripts',
           'skills', 'snapshot', 'overlay', 'licenses', 'tests')


def prepare(destination):
    destination = destination.resolve()
    if destination == ROOT:
        raise ValueError('A área de publicação deve ser separada do projeto.')
    destination.mkdir(parents=True, exist_ok=True)
    for name in INCLUDE:
        source = ROOT / name
        target = destination / name
        if source.is_dir():
            shutil.copytree(source, target, dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.git'))
        else:
            shutil.copy2(source, target)
    print('Arquivos preparados em:', destination)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', type=Path, required=True)
    prepare(parser.parse_args().destination)
