# Instalação

O destino de teste atual é **EndeavourOS mínimo**. Inicie a ISO, escolha o
instalador **online**, marque **No Desktop / sem desktop** e mantenha o sistema
base, rede/NetworkManager e ferramentas essenciais. Crie um usuário comum com
sudo. Use o bootloader e o gerador de initramfs oferecidos pelo EndeavourOS.
Depois da instalação, reinicie no disco e entre no TTY com esse usuário.

No EndeavourOS, o Gran mantém dracut e kernel-install e não instala mkinitcpio
nem Plymouth. Boot e criptografia ficam como configurados pela instalação
mínima; SDDM, autologin e desktop Gran continuam no plano padrão. A opção
`--boot` é recusada nesse destino para evitar trocar o fluxo de initramfs.


Para CachyOS, use sua ISO e selecione uma instalação mínima, sem desktop,
com internet, usuário comum e sudo. Reinicie no sistema instalado antes de usar
este projeto. Mantenha kernel e bootloader escolhidos pelo instalador CachyOS.
O Gran detecta CachyOS, usa os repositórios existentes e preserva seu boot por
padrão; não exige um preset mkinitcpio nesse fluxo.

Para Arch puro, use a ISO oficial e `archinstall` ou uma instalação manual.
Prepare o disco, a criptografia LUKS se desejada, o bootloader, o kernel, o
driver de GPU, internet e um usuário comum com sudo. Escolha um perfil mínimo.

O fluxo capturado no notebook é Limine -> Plymouth/LUKS -> SDDM autologin ->
Hyprland. Não é um registro EFI Direct Boot. Para reproduzir também o
bootloader, escolha Limine no Arch básico. O pós-instalador também consegue
ocultar o menu e ativar Plymouth em configurações existentes de systemd-boot
e GRUB; não troca o bootloader por outro.

Use o fuso America/Araguaina, BR ABNT2 e garanta que en_US.UTF-8 esteja gerado
para reproduzir o idioma da origem. Drivers são os do hardware de destino.

No EndeavourOS/CachyOS/Arch já instalado e reiniciado:

```bash
cd GranArch
sudo pacman -Syu
bash install.sh
bash install.sh --check
bash install.sh --install
```

O script instala pacotes oficiais, aplica desktop/skills, instala as ferramentas
mise e os aplicativos upstream, prepara os arquivos de login/boot/energia e
habilita os serviços para o próximo boot. Não reinicia automaticamente nem
inicia um display manager sobre a sessão em uso.

O autologin do SDDM elimina a segunda senha de login, como na origem. A senha
LUKS continua sendo solicitada pelo initramfs quando o disco é criptografado.
Sem LUKS não existe unlock de disco; nesse caso o autologin entra diretamente
no desktop. Use `--no-autologin` para manter a senha no greeter.

As etapas que alteram o boot exigem uma configuração de bootloader reconhecida
e um preset mkinitcpio no destino. Os hooks de armazenamento e criptografia
existentes são preservados; somente Plymouth é adicionado. Nenhum UUID,
PARTUUID, chave, resume_offset ou entrada EFI da origem é importado.

Para preservar partes do destino:

```bash
bash install.sh --install --no-boot --no-login
```

Depois do reboot, valide `gran doctor`. O caminho alternativo de sessão é
`gran session` em um TTY. Entre no Codex e no OpenCode novamente; não foram
importadas sessões ou tokens de autenticação.

Referências: [Archinstall](https://archinstall.archlinux.page/installing/guided.html),
[Hyprland](https://wiki.hypr.land/Getting-Started/Installation/),
[Quickshell](https://quickshell.org/docs/v0.3.2/guide/install-setup/).

## Dependências e diagnóstico

A lista de pacotes inclui ferramentas de compilação, Meson/Ninja/Sassc,
Inkscape/Xvfb/Xauth para renderização sem desktop, Python/Pillow/Cairo, schemas
GSettings/dconf, UPower, MIME e integração de aplicativos. As dependências
transitivas são resolvidas pelo pacman em uma atualização completa.
As pastas mise, dconf, aplicações, ícones, schemas GLib e cache são criadas
explicitamente, além das pastas dos arquivos exportados. A instalação Yaru
também cria a pasta de schemas antes do hook Meson.

`--check` não instala pacotes nem altera o destino. Ele consulta as bases locais
do pacman e exige Hyprland >=0.57.0 (configuração Lua) e Quickshell >=0.3.2.
Se uma base antiga não oferecer essas versões, atualize com `sudo pacman -Syu`.
Não substitua o compositor por uma versão anterior para contornar o diagnóstico.

O log fica em `~/.local/state/gran/install-backups/<data>/install.log` e informa
a linha em que a execução falhou. Depois da instalação, reinicie e execute
`gran doctor` dentro da sessão gráfica. O teste completo continua dependendo da
instalação mínima real na VM.

Referência para preservar o boot gerenciado do CachyOS:
[Boot Manager Configuration](https://wiki.cachyos.org/configuration/boot_manager_configuration/).

A integração do EndeavourOS foi baseada nas referências oficiais
[dracut](https://discovery.endeavouros.com/dracut/) e
[systemd-boot/kernel-install](https://discovery.endeavouros.com/systemd-boot/).
