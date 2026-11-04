#!/usr/bin/env python3
"""Offline verification: never installs packages or changes the current session."""
import ast, json, re, subprocess, sys, tomllib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
errors=[]
for path in ROOT.rglob('*'):
    if not path.is_file() or '.git' in path.parts or path.suffix=='.pyc':continue
    if any(p in path.parts for p in ('.agents','.codex','.aws','dist','__pycache__')):continue
    try:
        if path.suffix=='.py' or path.read_bytes().startswith((b'#!/usr/bin/env python3',b'#!/usr/bin/python3')): ast.parse(path.read_text(),filename=str(path))
        elif path.suffix=='.toml':tomllib.loads(path.read_text())
        elif path.suffix=='.json':json.loads(path.read_text())
        elif path.is_relative_to(ROOT/'iso/calamares') and path.suffix in ('.conf','.desc'):
            import yaml
            yaml.safe_load(path.read_text())
        elif path.name=='PKGBUILD' or path.suffix=='.sh' or path.read_bytes().startswith((b'#!/usr/bin/env bash',b'#!/bin/bash',b'#!/bin/sh')):
            subprocess.run(['bash','-n',str(path)],check=True)
        try:text=path.read_text()
        except UnicodeError:continue
        if path.is_relative_to(ROOT/'payload') and re.search(r'/home/granhat|/usr/bin/dnf|chromium-browser|Yaru|GranToolbar',text):
            raise ValueError('Dependência antiga ou caminho pessoal no payload')
    except (SyntaxError,ValueError,subprocess.CalledProcessError) as error: errors.append(f'{path.relative_to(ROOT)}: {error}')
config=tomllib.loads((ROOT/'payload/home/.config/noctalia/config.toml').read_text())
if config['shell']['font_family']!='sans-serif':errors.append('Noctalia precisa usar família padrão')
if abs(config['accessibility']['ui_scale']*14-11)>1e-6:errors.append('Fonte base precisa ser 11 px')
packages=[line for line in (ROOT/'manifests/packages.txt').read_text().splitlines() if line and not line.startswith('#')]
if len(packages)!=len(set(packages)):errors.append('Pacotes duplicados')
for package in packages:
    if not re.fullmatch(r'[a-z0-9][a-z0-9+_.-]*',package):errors.append('Pacote inválido: '+package)
audit=json.loads((ROOT/'manifests/package-audit.json').read_text())['packages']
for package in packages:
    if audit.get(package) is not True:errors.append('Pacote sem confirmação no catálogo Arch: '+package)
for name in ('hyprland','noctalia','linux-firmware','intel-ucode','sof-firmware','networkmanager','breeze-icons','mise'):
    if name not in packages:errors.append('Pacote obrigatório ausente: '+name)
if errors:
    print('\n'.join(errors),file=sys.stderr);sys.exit(1)
print(f'OK: sintaxe, manifests, {len(packages)} pacotes e perfil portátil. Boot e sessão Arch exigem teste em VM.')
