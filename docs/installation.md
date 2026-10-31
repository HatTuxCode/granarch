# Instalação

Use a ISO oficial do Arch e `archinstall` ou uma instalação manual.
Prepare o disco, a criptografia LUKS se desejada, o bootloader, o kernel, o
driver de GPU, internet e um usuário comum com sudo. Escolha um perfil mínimo.

O fluxo capturado no notebook é Limine -> Plymouth/LUKS -> SDDM autologin ->
Hyprland. Não é um registro EFI Direct Boot. Para reproduzir também o
bootloader, escolha Limine no Arch básico. O pós-instalador também consegue
ocultar o menu e ativar Plymouth em configurações existentes de systemd-boot
e GRUB; não troca o bootloader por outro.

Use o fuso America/Araguaina, BR ABNT2 e garanta que en_US.UTF-8 esteja gerado
para reproduzir o idioma da origem. Drivers são os do hardware de destino.

No Arch já instalado e reiniciado:

```bash
cd GranArch
bash install.sh
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
