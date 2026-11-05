#!/usr/bin/env python3
"""Build the reviewed AUR recipes as an ordinary user; install using pacman."""
import argparse,hashlib,json,os,pwd,shutil,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def install(user,output=None,build_only=False,only=None):
    if os.geteuid()!=0:raise SystemExit('Requer root no destino Arch; makepkg roda como usuário comum.')
    import platform
    if platform.freedesktop_os_release().get('ID')!='arch':raise SystemExit('Somente Arch Linux puro.')
    account=pwd.getpwnam(user)
    if account.pw_uid==0:raise SystemExit('Informe o usuário comum de destino.')
    packages=json.loads((ROOT/'manifests/desktop-packages.json').read_text())
    if only:packages={name:packages[name] for name in only}
    needed={}
    for name,metadata in packages.items():
        result=subprocess.run(['pacman','-Q',name],capture_output=True,text=True)
        if build_only or result.returncode or result.stdout.strip()!=name+' '+metadata['version']:needed[name]=metadata
    if not needed:return
    local=ROOT/'iso/packages'
    records=json.loads((local/'lock.json').read_text()) if (local/'lock.json').exists() else {}
    for name in list(needed):
        for artifact in sorted(local.glob(name+'-*.pkg.tar.zst')):
            if records.get(artifact.name)!=hashlib.sha256(artifact.read_bytes()).hexdigest():
                raise RuntimeError('Checksum do pacote local não confere: '+artifact.name)
            identity=subprocess.check_output(['pacman','-Qp',str(artifact)],text=True).strip()
            if identity!=name+' '+needed[name]['version']:continue
            if not build_only:
                subprocess.run(['pacman','-U','--needed','--noconfirm',str(artifact)],check=True)
                del needed[name]
                break
    if not needed:return
    dependencies=sorted({'base-devel',*(dep for data in needed.values() for dep in data['dependencies'])})
    subprocess.run(['pacman','-Syu','--needed','--noconfirm',*dependencies],check=True)
    env=os.environ.copy();env.update(HOME=account.pw_dir,USER=user,PATH='/usr/bin:/bin')
    cache=str(Path(account.pw_dir)/'.cache/granarch-sources')
    subprocess.run(['runuser','-u',user,'--','env','HOME='+account.pw_dir,'mkdir','-p',cache],check=True)
    env['SRCDEST']=cache
    if output:output.mkdir(parents=True,exist_ok=True)
    for name in needed:
        with tempfile.TemporaryDirectory(prefix='granarch-build-',dir='/var/tmp') as directory:
            build=Path(directory);shutil.copytree(ROOT/'packaging'/name,build,dirs_exist_ok=True)
            for path in [build,*build.rglob('*')]:os.chown(path,account.pw_uid,account.pw_gid)
            subprocess.run(['runuser','-u',user,'--','bash','-c','cd "$1"; exec makepkg --noconfirm --cleanbuild --noprogressbar','bash',str(build)],env=env,check=True)
            artifacts=[p for p in build.glob('*.pkg.tar.*') if not p.name.endswith('.sig') and '-debug-' not in p.name]
            if len(artifacts)!=1:raise RuntimeError('Pacote inesperado para '+name)
            artifact=artifacts[0]
            detected=subprocess.check_output(['pacman','-Qp',str(artifact)],text=True).strip()
            if detected!=name+' '+needed[name]['version']:raise RuntimeError('Nome ou versão de pacote inesperado')
            if output:shutil.copy2(artifact,output/artifact.name)
            if not build_only:subprocess.run(['pacman','-U','--needed','--noconfirm',str(artifact)],check=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('user');p.add_argument('--output',type=Path);p.add_argument('--build-only',action='store_true');p.add_argument('--only',action='append');a=p.parse_args()
    if a.build_only and not a.output:p.error('--build-only requer --output')
    install(a.user,a.output,a.build_only,a.only)
