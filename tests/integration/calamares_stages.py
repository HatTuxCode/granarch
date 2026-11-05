#!/usr/bin/env python3
"""Run the real custom jobs against an empty, disposable mounted Arch target.

Only the Calamares storage adapter is replaced; pacstrap, chroot, configuration,
package downloads and all user installation commands execute normally.
"""
import argparse,importlib.util,json,os,subprocess,sys,types
from pathlib import Path

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result)
    return result

def run(target):
    if os.geteuid()!=0 or not target.is_mount() or target==Path('/'):
        raise SystemExit('Requer root e um destino temporário montado, diferente de /.')
    if any(p.name!='lost+found' for p in target.iterdir()):
        raise SystemExit('O destino de teste precisa estar vazio.')
    source=Path('/opt/granarch')
    values={'rootMountPoint':str(target),'username':'installer-test'}
    sys.modules['libcalamares']=types.SimpleNamespace(globalstorage=types.SimpleNamespace(value=values.get))
    bootstrap=load('granbootstrap',source/'iso/calamares/modules/granbootstrap/main.py')
    profile=load('granprofile',source/'iso/calamares/modules/granprofile/main.py')
    print('TESTE: bootstrap real em destino vazio',flush=True)
    result=bootstrap.run()
    if result is not None:raise RuntimeError(result)
    subprocess.run(['arch-chroot',str(target),'useradd','-m','-G','wheel','-s','/bin/fish','installer-test'],check=True)
    # The fixture replaces the locale/user view steps, never creates passwords.
    with (target/'etc/locale.gen').open('a') as output:output.write('\npt_BR.UTF-8 UTF-8\n')
    (target/'etc/locale.conf').write_text('LANG=pt_BR.UTF-8\n')
    (target/'etc/vconsole.conf').write_text('KEYMAP=br-abnt2\n')
    subprocess.run(['arch-chroot',str(target),'locale-gen'],check=True)
    print('TESTE: granprofile real com usuário novo',flush=True)
    result=profile.run()
    if result is not None:raise RuntimeError(result)
    home=target/'home/installer-test'
    uid=int(subprocess.check_output(['arch-chroot',str(target),'id','-u','installer-test'],text=True))
    assert (home/'.cache').stat().st_uid==uid, 'Cache pertence ao usuário errado'
    assert 'NoExtract' not in (target/'etc/pacman.conf').read_text()
    locales=subprocess.check_output(['arch-chroot',str(target),'locale','-a'],text=True)
    assert 'pt_BR.utf8' in locales,locales
    print(json.dumps({'result':'success','bootstrap':'real','granprofile':'real','cache_owner':'correct','locale':'pt_BR.utf8','target':str(target)}),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('target',type=Path);run(p.parse_args().target.resolve())
