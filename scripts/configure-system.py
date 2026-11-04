#!/usr/bin/env python3
"""Root-only configuration in an installed Arch target (including arch-chroot)."""
import argparse, os, pwd, shutil, subprocess, tempfile
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def configure(user, preserve_locale=False):
    if os.geteuid()!=0:raise SystemExit('Requer root no destino Arch')
    account=pwd.getpwnam(user);home=Path(account.pw_dir)
    if account.pw_uid==0:raise ValueError('Usuário comum obrigatório')
    backup=Path('/var/backups/granarch')/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    def write(path,data,mode=0o644):
        path=Path(path)
        if path.exists():
            saved=backup/path.relative_to('/');saved.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,saved)
        path.parent.mkdir(parents=True,exist_ok=True);path.write_text(data);path.chmod(mode)
    for source in (ROOT/'payload/system').rglob('*'):
        if source.is_file():write('/'+str(source.relative_to(ROOT/'payload/system')),source.read_text().replace('@HOME@',str(home)),source.stat().st_mode&0o777)
    write('/usr/local/bin/gran-session',f'#!/bin/sh\nexec "{home}/.local/share/gran/bin/gran-session" "$@"\n',0o755)
    write('/usr/share/wayland-sessions/granarch.desktop','[Desktop Entry]\nName=GranArch\nComment=Hyprland + Noctalia\nExec=/usr/local/bin/gran-session\nType=Application\nDesktopNames=Hyprland\n')
    write('/etc/sddm.conf.d/20-granarch.conf','[General]\nDisplayServer=x11\n\n[Autologin]\nUser=\nSession=granarch.desktop\n')
    # Arch SDDM PAM stack already uses system-login; add only keyring hooks.
    pam=Path('/etc/pam.d/sddm');text=pam.read_text()
    if 'pam_gnome_keyring.so' not in text:
        write(pam,text+'\nauth optional pam_gnome_keyring.so\nsession optional pam_gnome_keyring.so auto_start\n')
    write('/etc/sudoers.d/20-granarch-wheel','%wheel ALL=(ALL:ALL) ALL\n',0o440)
    subprocess.run(['visudo','-cf','/etc/sudoers.d/20-granarch-wheel'],check=True)
    subprocess.run(['usermod','-aG','wheel',user],check=True)
    subprocess.run(['usermod','-s','/usr/bin/fish',user],check=True)
    if not preserve_locale:
        write('/etc/locale.conf','LANG=pt_BR.UTF-8\n')
        write('/etc/vconsole.conf','KEYMAP=br-abnt2\n')
        locales=Path('/etc/locale.gen').read_text()
        for locale in ('pt_BR.UTF-8 UTF-8','en_US.UTF-8 UTF-8'):
            if locale not in locales.splitlines():locales+='\n'+locale+'\n'
        write('/etc/locale.gen',locales)
        subprocess.run(['locale-gen'],check=True)
        subprocess.run(['ln','-sf','/usr/share/zoneinfo/America/Araguaina','/etc/localtime'],check=True)
    # Only ASUS exposes this module parameter; no forced driver loading.
    if 'ASUS' in Path('/sys/class/dmi/id/sys_vendor').read_text().upper():
        write('/etc/modprobe.d/granarch-asus.conf','options asus_wmi fnlock_default=N\n')
    subprocess.run(['systemctl','enable','NetworkManager.service','bluetooth.service','power-profiles-daemon.service','docker.service','libvirtd.service','firewalld.service','sddm.service','gran-charge-limit.service','gran-browser-theme.path'],check=True)
    print('Backup do sistema:',backup)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('user');p.add_argument('--preserve-locale',action='store_true');args=p.parse_args();configure(args.user,args.preserve_locale)
