"""Apply the captured environment after Calamares creates the real user."""
from pathlib import Path
import shutil,subprocess
import libcalamares

def run():
    target=Path(libcalamares.globalstorage.value('rootMountPoint'))
    user=libcalamares.globalstorage.value('username')
    import re
    if not isinstance(user,str) or not re.fullmatch('[a-z_][a-z0-9_-]{0,30}',user):return ('Usuário inválido','Não foi possível obter o usuário de destino.')
    relative=f'/home/{user}/.cache/granarch-installer'
    stage=target/relative.lstrip('/');stage.parent.mkdir(parents=True,exist_ok=True)
    shutil.copytree('/opt/granarch',stage,dirs_exist_ok=True)
    commands=[
        ('verificar versões', ['python3',relative+'/scripts/check-versions.py']),
        ('configurar serviços', ['python3',relative+'/scripts/configure-system.py',user,'--preserve-locale']),
        ('preparar permissões', ['chown','-R',user+':'+user,relative]),
        ('instalar perfil e aplicativos', ['runuser','-u',user,'--','env','-u','DBUS_SESSION_BUS_ADDRESS','-u','HYPRLAND_INSTANCE_SIGNATURE',f'HOME=/home/{user}',f'USER={user}','bash',relative+'/scripts/user-install.sh'])]
    for label,command in commands:
        result=subprocess.run(['arch-chroot',str(target),*command])
        if result.returncode:return ('Falha ao configurar o desktop','A etapa '+label+' falhou. Consulte o log antes de reiniciar.')
    return None
