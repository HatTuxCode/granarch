"""Install only Arch official packages into Calamares' mounted target."""
from pathlib import Path
import subprocess
import libcalamares

def run():
    target=Path(libcalamares.globalstorage.value('rootMountPoint'))
    if str(target)=='/' or not target.is_mount():return ('Destino inválido','A raiz precisa estar montada pelo Calamares.')
    project=Path('/opt/granarch')
    packages=[p for p in (project/'manifests/packages.txt').read_text().splitlines() if p and not p.startswith('#')]
    packages+=['grub','efibootmgr','os-prober','dosfstools','e2fsprogs','btrfs-progs','cryptsetup']
    # pacstrap manages signatures and required pseudo-filesystems. No distro repos.
    result=subprocess.run(['pacstrap','-K',str(target),*packages])
    if result.returncode:return ('Falha ao instalar pacotes Arch','Confira a conexão e os mirrors; consulte o log do Calamares.')
    return None
