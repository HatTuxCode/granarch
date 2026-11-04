# GranArch

Instalador de **Arch Linux puro**, com o ambiente da máquina GranHat/Fedora
migrado para pacman: Hyprland Lua, Noctalia nativo v5, programas, atalhos,
políticas de energia e integração de temas. O instalador gráfico usa **Calamares**,
o mesmo framework utilizado pelo EndeavourOS, com configuração própria.

O projeto foi reconstruído a partir da configuração efetiva de 04/11/2026.
O código antigo está preservado na branch `archive/before-native-arch-*`.
O Fedora instalado não é alterado pelos comandos de verificação ou de build.

**Estado:** código e perfil preparados; verificações locais passaram.
A ISO ainda precisa ser compilada num host Arch e a instalação completa precisa
ser testada numa VM UEFI. Não há ISO publicada nem boot comprovado.

## O ambiente instalado

- Hyprland >= 0.57.1 com Lua; Noctalia >= 5.4.1 nativo, sem Quickshell.
- Monitor em **125%**. Noctalia usa sua família padrão `sans-serif`, base lógica
  **11 px** (`ui_scale=11/14`) e tamanhos relativos nativos. A barra também recebe
  base de 11 px. Isso corresponde a cerca de 13,75 pixels físicos em escala 125%.
  Os ajustes pessoais de fontes de Kitty, GTK, Qt e Zen não são importados;
  esses aplicativos conservam suas fontes e tamanhos nativos.
- Barra com disposição efetiva da origem: launcher, bolinhas dos workspaces e
  janela ativa; relógio brasileiro e clima; tray, RAM, temperatura, CPU,
  atualizações, Bluetooth, rede, volume, brilho, energia, bateria e sessão.
  Dimensões, margens, opacidade e cantos preservados; monitores sem barrinhas.
- Paleta Nord compartilhada entre Noctalia, GTK, Qt/Dolphin, Kitty, btop, Zen e
  Chromium; modo noturno sempre ativo em 4500 K.
- Desenho original das pastas **KDE Breeze**, com tom verde-cinza **#8fa89b**.
  O tema local `GranBreezeNord` altera apenas a cor de acento dos SVGs de pastas;
  demais ícones são herdados do Breeze. Cursor Breeze. **Sem Yaru**.
- Janelas com opacidade 90%/60%, blur, raio 4, bordas 2, gaps 3/6 e regras atuais.
  Diálogos do virt-manager centralizados em 900×600; consoles seguem o layout.
- Todos os atalhos do `hyprland.lua` atual, incluindo Codex, OpenCode, TUIOS,
  GranControl, terminal, Dolphin, Docker, screenshots e clipboard adaptado.
- Dwindle e scrolling; workspace vazio extra e indicadores de bolinhas.
- Touchpad com **arraste/seleção com três dedos** (`drag_3fg=1`), toque para clicar
  e rolagem natural. Teclas Fn de áudio, microfone, tela, luz do teclado e touchpad.
- Perfis: performance na tomada, balanced na bateria, power-saver até 25%, com
  fallback para capacidades reais. Limite de carga 95% quando suportado.
  Luz do teclado apaga após 30 s na bateria; tela após 20 min em bateria <=25%.
  Tampa suspende inclusive na tomada/dock; bloqueio solicitado antes de suspender.
- Kitty, fish, Dolphin, Chromium, Zen, imv, btop, fastfetch, Neovim, tmux,
  ferramentas de terminal, Docker/lazydocker e virtualização QEMU/libvirt.
  Codex/OpenCode/lazydocker/Starship via **mise aqua**, sem npm postinstall.
  Zen e TUIOS: releases oficiais com SHA-256 fixado no manifesto.
- SDDM com senha e GNOME Keyring; Docker sem adicionar usuário ao grupo docker.

A lista de pacotes do Fedora está em `manifests/source-fedora-packages.txt` para
rastreabilidade. Bibliotecas e pacotes internos da distribuição são substituídos
pelas dependências Arch; não se tenta instalar RPMs no Arch. O manifesto instalável
é `manifests/packages.txt`. Não são copiados logins, perfis de navegador, Wi-Fi,
chaves, histórico, clipboard ou dados pessoais. Contas precisam de novo login.

## Gerar e baixar pelo GitHub

O workflow **Build GranArch ISO** compila o Calamares e gera a ISO em um
container Arch privilegiado num runner descartável do GitHub. Não exige VM local.
Executa em pushes da `main` que alterem o instalador, ou manualmente em
**Actions → Build GranArch ISO → Run workflow**.

Após a execução ficar verde, abra **Artifacts → granarch-iso-N** e baixe a ISO
com `SHA256SUMS`. O artefato fica disponível por sete dias; requer login no
GitHub para download. O log também é disponibilizado quando o build falha.
Isso gera a imagem; o boot e uma instalação completa ainda precisam ser testados
em VM antes de instalar no notebook. Não há publicação automática em Releases.

## Gerar a ISO com Calamares

Use uma VM ou máquina **Arch puro x86_64**, com espaço disponível para a ISO e
compilação. Não execute o instalador sobre a máquina Fedora de referência.

```bash
sudo pacman -Syu --needed base-devel git archiso cmake ninja
cd packaging/calamares
makepkg -s
cd ../..
sudo scripts/build-iso.sh packaging/calamares/calamares-3.4.2-1-x86_64.pkg.tar.zst
```

A receita compila o Calamares upstream 3.4.2 com checksum fixo. O pacote é colocado
num repositório local **somente durante o build da ISO**, sem adicionar repositório
EndeavourOS, CachyOS ou Omarchy ao destino. A base e os programas vêm dos
repositórios oficiais Arch. A ISO e `SHA256SUMS` saem em `dist/`.

O build usa o perfil `releng` do archiso instalado, com desktop live Hyprland e
Noctalia. Na sessão live, abra **Instalar GranArch** pelo launcher (`Super+Space`).
O usuário live tem login automático apenas na ISO; o destino usa senha.

O Calamares apresenta idioma, teclado, particionamento, usuário e resumo antes
de gravar. O fluxo é **online**: baixa pacotes Arch com `pacstrap` e aplica o perfil
após criar o usuário. É necessária internet também para mise, Zen e TUIOS.
Não há particionamento silencioso por scripts. Criptografia e boot pelo Calamares
precisam de teste específico em VM antes de serem considerados suportados.

## Alternativas pelo terminal

Em um Arch puro já instalado, com usuário comum, sudo, internet e boot funcional:

```bash
./install.sh --plan
./install.sh --verify
./install.sh --install
```

A instalação substitui configurações de desktop com backup em
`~/.local/state/gran/backups/`; configurações administrativas têm backup em
`/var/backups/granarch/`. Overrides do Noctalia são arquivados para não sobrepor o
perfil solicitado. Pacotes atualizam com `pacman -Syu`, evitando upgrade parcial.

O modo `--live` é uma alternativa avançada à interface gráfica: exige a ISO
oficial Arch em UEFI, raiz ext4 **já preparada** em `/mnt` e ESP FAT32 vazia em
`/mnt/boot`. Não particiona nem formata. Aceita raiz LUKS previamente aberta,
usando o UUID descoberto no destino. Exige confirmação `INSTALAR`:

```bash
./install.sh --live /mnt nomeusuario nomedamaquina
```

As senhas são digitadas diretamente em `passwd`, sem argumentos ou arquivos.
O modo terminal usa systemd-boot e initramfs systemd/sd-encrypt; o Calamares usa
GRUB. Não reaproveite UUIDs, partições ou arquivos de boot da máquina de origem.

## Validar e testar

```bash
./install.sh --verify
python3 -m unittest discover -s tests -v
```

Requer Python 3.11+ e PyYAML (`python-yaml` no Arch).

Os testes cobrem aplicação recuperável, proteção contra links que escapam do HOME,
portabilidade dos caminhos, cor das pastas sem mudar o desenho, rejeição de
checksum incorreto, recusa de instalação no Fedora e validadores nativos em HOME
isolado. O verificador também confere sintaxe, manifests e pacotes obrigatórios.

Após instalar numa VM e entrar em **GranArch** no SDDM:

```bash
gran doctor
hyprctl configerrors
noctalia config export full
nmcli device
wpctl status
```

Veja o roteiro em [docs/validation.md](docs/validation.md). Validação de sintaxe
não comprova boot, comportamento do Calamares, equivalência visual, Wi-Fi,
suspensão, bateria ou gestos reais.

## Estrutura e créditos

`payload/` contém somente arquivos selecionados da origem, com `@HOME@` substituído
no destino. `scripts/` instala e valida; `iso/` configura Calamares e a sessão live;
`packaging/` contém a receita do Calamares. `AGENTS.md` registra as preferências.

Hyprland, Noctalia, Calamares, KDE Breeze e os aplicativos mantêm suas respectivas
licenças upstream. O runtime Gran preserva seu arquivo LICENSE; utilitários
originalmente derivados de Omarchy mantêm a atribuição MIT. O wallpaper e os assets
capturados são referência pessoal; revisar direitos de redistribuição antes de
publicar a ISO.
