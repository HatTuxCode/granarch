#!/usr/bin/env python3
"""Install locked official Linux binaries; reject unverified or unsafe archives."""
from datetime import datetime, timezone
import hashlib, json, os, re, shutil, subprocess, sys, tarfile, tempfile
from pathlib import Path
from urllib.request import Request, urlopen


def download(asset, target):
    if not asset['url'].startswith('https://github.com/') or not re.fullmatch('[0-9a-f]{64}',asset['sha256']):
        raise ValueError('Fonte ou SHA-256 inválido')
    digest=hashlib.sha256(); size=0
    with urlopen(Request(asset['url'],headers={'User-Agent':'GranArch'}),timeout=90) as response,target.open('wb') as output:
        while chunk:=response.read(1024*1024):
            size+=len(chunk)
            if size>1024**3: raise ValueError('Download excessivo')
            digest.update(chunk);output.write(chunk)
    if digest.hexdigest()!=asset['sha256']: raise ValueError('SHA-256 não confere')


def install(name,home):
    if name!='tuios':raise ValueError('Aplicativo portátil não suportado: '+name)
    data=json.loads((home/'.local/share/gran/default/upstream-lock.json').read_text());asset=data[name]
    apps=home/'.local/share/gran/apps';apps.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=apps) as temp:
        temp=Path(temp);archive=temp/'download';download(asset,archive)
        extracted=temp/'unpacked';extracted.mkdir()
        with tarfile.open(archive) as tar: tar.extractall(extracted,filter='data')
        binary=next((p for p in extracted.rglob(name) if p.is_file() and not p.is_symlink()),None)
        if binary is None: raise ValueError(f'Binário {name} ausente')
        destination=apps/name
        if destination.exists():
            backup=home/'.local/state/gran/backups'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')/name
            backup.parent.mkdir(parents=True,exist_ok=True);shutil.move(destination,backup)
        shutil.move(extracted,destination)
        binary=destination/binary.relative_to(extracted)
        binary.chmod(0o755)
    localbin=home/'.local/bin';localbin.mkdir(parents=True,exist_ok=True)
    command=name
    launcher=localbin/command
    if launcher.exists() or launcher.is_symlink():
        backup=home/'.local/state/gran/backups'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')/command
        backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(launcher,backup,follow_symlinks=True)
        launcher.unlink()
    launcher.symlink_to(binary)
    print(name,asset['version'],'instalado e verificado')
if __name__=='__main__':
    if os.geteuid()==0: raise SystemExit('Execute como usuário comum')
    for name in sys.argv[1:] or ['tuios']:
        if name=='zen':raise SystemExit('Zen é gerenciado como pacote zen-browser-bin pelo instalador.')
        install(name,Path.home())
