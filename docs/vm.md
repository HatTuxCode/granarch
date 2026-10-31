# VM de teste

A VM está em `vm/`: disco qcow2 próprio e esparso de 64 GB, UEFI/OVMF,
2 CPUs, 2 GB de RAM, rede NAT e vídeo VirtIO com aceleração 3D.
Nenhum disco físico, pasta pessoal ou dispositivo do notebook é repassado.
O segundo CD contém somente o pacote GranArch e seu checksum.

Abra no **terminal do notebook**:

```bash
cd /home/hattux/Projects/GranArch
bash scripts/vm.sh open
```

Isso registra a VM na conexão libvirt do usuário e abre seu console no
Virt Manager. A conexão é `qemu:///session`, separada da conexão de sistema.
Como alternativa, `bash scripts/vm.sh direct` abre a mesma VM diretamente no
QEMU/GTK; use apenas uma dessas formas por vez.

O ambiente do agente não tem acesso a KVM/libvirt do host, portanto preparar
os arquivos aqui não significa que a VM já tenha sido iniciada no desktop.

## Dentro da VM

Na ISO Arch, execute `archinstall`. Selecione **somente /dev/vda**, o disco
virtual de 64 GB. Use perfil mínimo, criptografia LUKS para testar o unlock,
um usuário comum com sudo, NetworkManager e um bootloader suportado.
Selecione Limine se quiser reproduzir o bootloader do notebook; systemd-boot
também é suportado pelo pós-instalador. Gere `en_US.UTF-8`.

Depois de instalar, reinicie no disco virtual. Se a ISO voltar a iniciar,
desconecte o CD Arch no Virt Manager ou escolha a entrada do disco no UEFI.
O segundo CD tem o rótulo `GRANARCH` e pode continuar conectado.

Entre com seu usuário comum e copie o pacote do CD:

```bash
sudo mkdir -p /mnt/granarch
sudo mount /dev/disk/by-label/GRANARCH /mnt/granarch
mkdir -p ~/GranArch-test
cp /mnt/granarch/granarch-bootstrap.tar.gz* ~/GranArch-test/
cd ~/GranArch-test
sha256sum -c granarch-bootstrap.tar.gz.sha256
tar -xzf granarch-bootstrap.tar.gz
cd GranArch
bash install.sh
bash install.sh --install
```

Reinicie e confira boot/unlock, login, barra, menu, lançador e cores. Rode
`gran doctor`. Fn Lock, iluminação física e carga de bateria só podem ser
validados depois no notebook; a VM não recebe esses dispositivos.

Para desligar: use o menu System da VM ou `bash scripts/vm.sh stop` no host.
Para preparar novamente após atualizar o pacote:

```bash
bash scripts/vm.sh prepare
```

O comando preserva o disco e o NVRAM existentes e atualiza o CD GranArch.
Faça essa atualização com a VM desligada. Os arquivos da VM não entram no
pacote distribuível nem no controle de versão.
