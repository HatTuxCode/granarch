# VM de teste

A VM EndeavourOS está em `vm/endeavouros/`: disco qcow2 próprio e esparso de 64 GB, UEFI/OVMF,
2 CPUs, 3 GB de RAM, rede NAT e vídeo VirtIO com aceleração 3D.
Nenhum disco físico, pasta pessoal ou dispositivo do notebook é repassado.
O segundo CD contém somente o pacote GranArch e seu checksum.

Abra no **terminal do notebook**:

```bash
cd /home/hattux/Projects/GranArch
bash scripts/vm.sh replace-cachyos
```

Esse comando encerra e remove somente a antiga VM CachyOS `granarch-test`,
confere seu UUID e abre a nova `granarch-endeavouros`. O disco e o NVRAM da
VM antiga serão apagados; a ISO original em Downloads é preservada. A remoção
precisa ser feita no terminal do notebook porque o ambiente do agente não
consegue acessar o socket libvirt do host. Se a VM antiga não estiver no
Virt Manager, ela pode estar na conexão de usuário em vez da conexão de sistema.

Depois dessa troca, use `bash scripts/vm.sh open` normalmente.

Isso registra a VM na conexão libvirt do usuário e abre seu console no
Virt Manager. A conexão é `qemu:///session`, separada da conexão de sistema.
Para abrir manualmente a conexão correta: `virt-manager --connect qemu:///session`.
Como alternativa, `bash scripts/vm.sh direct` abre a mesma VM diretamente no
QEMU/GTK; use apenas uma dessas formas por vez.

O ambiente do agente não tem acesso a KVM/libvirt do host, portanto preparar
os arquivos aqui não significa que a VM já tenha sido iniciada no desktop.

## Dentro da VM

Na ISO EndeavourOS, escolha o instalador **online** e a opção
**No Desktop / sem desktop**. Mantenha o sistema base, NetworkManager e os
pacotes essenciais; configure usuário comum com sudo.
Selecione **somente /dev/vda**, o disco
virtual de 64 GB. Use perfil mínimo, criptografia LUKS para testar o unlock,
um usuário comum com sudo e NetworkManager. Mantenha o kernel e o bootloader
do EndeavourOS. Gere `en_US.UTF-8`.

Depois de instalar, reinicie no disco virtual. Se a ISO voltar a iniciar,
desconecte o CD EndeavourOS no Virt Manager ou escolha a entrada do disco no UEFI.
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
sudo pacman -Syu
bash install.sh
bash install.sh --check
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

A preparação procura `~/Downloads/EndeavourOS*.iso`, priorizando o arquivo mais
recente. Para escolher explicitamente:

```bash
bash scripts/build-bundle.sh
bash scripts/vm.sh prepare --iso ~/Downloads/EndeavourOS_Titan-Nova-2026.08.15.iso
```

No EndeavourOS o script preserva o boot, o kernel e o gerador de initramfs por
padrão, sem instalar mkinitcpio sobre dracut. O teste dessa VM valida o boot nativo do EndeavourOS seguido do SDDM/Gran.

O comando preserva o disco e o NVRAM existentes e atualiza o CD GranArch.
Faça essa atualização com a VM desligada. Os arquivos da VM não entram no
pacote distribuível nem no controle de versão.
