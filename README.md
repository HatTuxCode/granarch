# GranArch

Pós-instalador para um EndeavourOS mínimo, Arch Linux enxuto ou CachyOS com o seu desktop atual, portado para
**Gran**. A ISO será montada depois da validação e dos ajustes.

O sistema não usa repositório, mirror, chave ou pacote do Omarchy. Hyprland,
Quickshell, Kitty, fish, mise, SDDM e Plymouth são pacotes oficiais do Arch,
construídos dos projetos upstream. Zen vem dos releases oficiais de
`zen-browser/desktop`, com SHA-256 verificado. Os ícones e o cursor Yaru são
compilados de `ubuntu/yaru`. Veja [as fontes](manifests/sources.json).

A configuração e o código do shell foram derivados da instalação atual, com
atribuição e licença preservadas, e portados para `gran`. Os mecanismos de
repositório, provisionamento, migração e factory reset da distribuição de origem
foram removidos. Os motores Hyprland e Quickshell não são forks dessa distribuição.

## O que será instalado

- Nord, wallpaper atual, sua barra Quickshell, plugins, blur, opacidade, gestos,
  monitores, teclado e **todos os módulos de atalhos originais**.
- Zen padrão, Kitty com o cursor trail atual, todos os seus ajustes e fish.
- Node LTS, Codex CLI e OpenCode pelo mise.
- Skills `gran`, `gran-app` e `gran-diagnose`, descobertas por Codex e OpenCode
  em `~/.agents/skills`.
- Lançador de aplicativos herdado e menu amplo com Setup, instalar/remover
  pacotes, Web Apps, AUR e catálogo opcional. Veja [o menu](docs/menu.md).
- Boot silencioso, tema Plymouth atual para o unlock do disco e SDDM com
  autologin na sessão Gran, reproduzindo o fluxo deste notebook.
- As políticas de energia e backlight do notebook, incluindo carga máxima 95%,
  luz do teclado após 30s na bateria e regra da tela de 20min com bateria <=25%.
- A paleta compartilhada em GTK3, GTK4/libadwaita, Qt por GTK/Fusion, Kitty,
  programas de terminal e a interface do Zen.

Os atalhos vêm da configuração Gran atual do notebook, com seus caminhos
adaptados para o usuário de destino. `Super+Shift+T` e `Super+Enter` usam o
terminal padrão Kitty; `Ctrl+Super+Alt+T` abre o btop flutuante e centralizado.
Aplicativos opcionais referenciados pelos atalhos, como TUIOS e GranCtrl,
continuam dependendo da instalação desses aplicativos.

## Usar no EndeavourOS mínimo ou Arch novo

Para baixar pelo repositório:

```bash
sudo pacman -Syu --needed git
git clone https://github.com/HatTuxCode/granarch.git
cd granarch
bash install.sh --verify
bash install.sh --check
bash install.sh --install
```

Execute os comandos como usuário comum; somente o pacman e as etapas internas
que precisam de privilégio usam sudo. Se `--check` falhar, corrija o erro antes
de executar `--install`.

Se o repositório for privado, autentique seu acesso GitHub antes de cloná-lo.
Não é necessário baixar o pacote de distribuição quando o projeto é clonado.

Instale um EndeavourOS mínimo (instalação online, opção sem desktop) ou Arch básico x86_64 com bootloader funcionando, internet, usuário comum,
sudo e locale `en_US.UTF-8`. Para conservar o unlock de disco como no notebook
atual, escolha criptografia LUKS durante a instalação básica. O script não
particiona nem transforma um disco existente em criptografado.

Copie a pasta inteira para o Arch novo ou use o pacote pronto:

```bash
tar -xzf granarch-bootstrap.tar.gz
cd GranArch
bash install.sh                    # apenas visualizar
bash install.sh --verify
bash install.sh --check              # conferir o destino, sem instalar
bash install.sh --install          # assistente de pós-instalação
```

O assistente mostra o plano antes de pedir `INSTALAR` e mantém as confirmações do
pacman. Os pacotes estão em [manifests/packages.txt](manifests/packages.txt);
ASUS/Intel recebem os componentes de hardware pertinentes. Não instale sobre a
máquina de origem: o assistente recusa convertê-la.

Após reiniciar, o SDDM inicia a sessão Gran conforme o plano. Pelo TTY, a
alternativa é `gran session`. Execute `gran doctor` dentro do desktop.

No EndeavourOS, o instalador preserva dracut, kernel-install, o kernel e o
bootloader. Não instala mkinitcpio/Plymouth nem modifica o boot nesse fluxo;
o SDDM e a sessão Gran são configurados normalmente. Use a instalação online
com **No Desktop / sem desktop**, usuário comum, sudo e NetworkManager.

No CachyOS, os pacotes seguem a prioridade dos repositórios já configurados,
incluindo as variantes otimizadas. Kernel, initramfs e boot são preservados por
padrão. O visual Plymouth do Gran fica restrito ao fluxo de boot suportado do
Arch; `--boot` exige mkinitcpio e boot sem gerenciadores da distribuição; não é suportado no EndeavourOS.

O instalador cria as pastas auxiliares mesmo em um HOME vazio, verifica os
pacotes e versões disponíveis antes de aplicar o desktop e registra a execução
em `~/.local/state/gran/install-backups/<data>/install.log`. A pré-verificação usa
as bases locais do pacman; se estiverem antigas, execute `sudo pacman -Syu`.

Opções de instalação: `--check`, `--boot`, `--no-boot`, `--no-login`, `--no-autologin`,
`--no-change-shell`, `--no-services` e `--no-yaru`.
Confira [instalação](docs/installation.md) e
[boot, energia e cores](docs/boot-power-theme.md).

## Atualizar a aparência em uma instalação existente

Depois de publicar esta versão, no EndeavourOS que já tem o GranArch:

```bash
cd ~/granarch
git pull --ff-only
bash scripts/update-desktop.sh
```

Essa atualização instala fastfetch e aplica o G desenhado, o símbolo usado no
terminal, o painel Sobre, o ícone/lançador oficial do Zen, o fosco do Files e a
barra nativa em uso no notebook. Também instala/verifica o OpenCode oficial.
A atualização também restaura os atalhos atuais do notebook e os aliases fish,
salvando as versões anteriores em `~/.local/state/gran/shortcut-backups`.
Monitores, perfil do navegador, contas e favoritos são preservados.
A seleção antiga `hattux.bar` é migrada para `gran.bar`, preservando a disposição
dos widgets: laterais de 6 px, topo de 3 px e cantos seguindo o arredondamento
do Hyprland (4 px no padrão atual).
Os arquivos substituídos ficam em `~/.local/state/gran/appearance-backups`;
CSS e `user.js` existentes recebem backups antes das alterações de tema.
Feche/reabra Zen e Files e saia/entre na sessão para recarregar a barra.

A referência capturada do Zen é **1.24b**, com modo compacto ao iniciar e a
paleta Nord. Novas instalações usam esse release oficial com SHA-256 verificado;
`gran app update zen` continua consultando o release oficial mais recente.
A atualização de aparência repara o Zen já instalado sem fazer downgrade nem
copiar perfis do notebook. O ícone vem do próprio pacote oficial do navegador,
e não de uma imagem genérica do tema.

## Comandos

```fish
gran update              # pacman + mise + programas upstream já gerenciados
gran doctor              # programas, configuração e sessão
gran commands            # comandos reais disponíveis
gran sources             # origem dos componentes
gran skills list         # skills disponíveis para as IAs
gran theme sync          # regenerar paleta compartilhada
gran app sources         # fontes dos aplicativos gerenciados diretamente
gran app update installed
gran launch apps         # grade de aplicativos herdada
gran pkg install         # buscar e instalar pacotes
gran webapp install      # criar um aplicativo de site
gran setup keyboard     # assistente de layout do teclado
```

Configurações: `~/.config/hypr`, `~/.config/gran`, `~/.config/kitty` e
`~/.config/fish`. Estado do tema: `~/.local/state/gran/current`.
Fontes e utilitários locais: `$GRAN_PATH`, normalmente `~/.local/share/gran`.

O mise gerencia Node, Codex e OpenCode. Pacman gerencia os componentes do Arch.
`gran update` não substitui os seus arquivos de desktop por templates upstream.
Alterações do próprio desktop são mantidas neste projeto.

## Modificar e gerar o pacote

Edite `overlay/`, `skills/`, os manifests e os scripts de aplicação. A captura
portada fica separada em `snapshot/`. Na máquina de origem, recapture com:

```bash
python scripts/capture-desktop.py --replace
bash install.sh --verify
```

A política de hardware documentada fica em
[manifests/notebook.json](manifests/notebook.json); revise-a ao alterar os padrões
da instalação de origem. Para gerar o pacote completo:

```bash
bash scripts/build-bundle.sh
```

O resultado é `dist/granarch-bootstrap.tar.gz`, com arquivo SHA-256 ao lado.

## Validação e limites atuais

Os testes locais verificam aplicação em diretórios temporários, backups,
reaplicação, conservação dos atalhos, nomes Gran, fontes, integridade, download
verificado e preparação de boot sem transplantar identificadores de disco.
Isso não comprova boot em um Arch novo. O fluxo completo de boot, unlock,
suspensão, hardware e o visual do Quickshell oficial ainda precisam ser
validados em VM e depois no notebook. Veja [validação](docs/validation.md).

A API Lua de referência é Hyprland >=0.57 e o shell usa Quickshell >=0.3.2.
Uma diretiva do loader modificado foi removida; não é necessário esse patch.
A regra de bateria foi adaptada à escala 0..1 usada pelo UPower do Quickshell
oficial, mantendo o limite configurado em 25%.

Os widgets de Proton VPN e câmera são preservados, mas seus backends/modelos não
vêm com a base. O widget `crmne.lyrics` já não tem plugin correspondente na
origem. Ditado e gravação avançada precisam das suas ferramentas opcionais.
Titlebars opcionais podem ser instaladas do repositório oficial de plugins
Hyprland por `gran plugin hyprbars install`, após instalar hyprpm e as
dependências de compilação. Não há pacote de titlebars da distribuição de origem.

Aplicativos que desenham seus próprios temas ou rodam em sandboxes podem ignorar
a paleta do sistema e precisam de integração própria. Páginas web, documentos e
imagens mantêm suas cores. O perfil novo do Zen recebe a paleta antes do primeiro
uso; perfis existentes recebem os imports de CSS sem copiar logins ou sessões.

## Dados e licenças

Não foram copiados credenciais, contas, perfis do navegador, chaves SSH/GPG,
histórico de shell, notificações ou clipboard. A localização configurada do
widget de clima e os padrões do notebook são preferências preservadas.

Backups: `~/.local/state/gran/backups`, `install-backups`, `theme-backups` e
`/var/backups/gran`. Eles preservam arquivos, não desfazem transações de pacotes.

A origem dos componentes derivados é [Omarchy](https://github.com/omacom/omarchy),
sob [MIT](licenses/omarchy-MIT.txt). Créditos, autores e licenças dos plugins são
mantidos. Antes de publicar uma ISO, revisar também licenças de plugins,
wallpaper, fontes e demais assets. As menções upstream em créditos não são
dependências de instalação ou atualização.

## Reparar OpenCode instalado pela versão anterior

Se `opencode` informar que o postinstall de `opencode-ai` não rodou, depois de
publicar e baixar esta versão:

```bash
cd ~/granarch
git pull --ff-only
bash scripts/repair-opencode.sh
```

O reparo usa o binário oficial `aqua:anomalyco/opencode` pelo mise, executa
`opencode --version` e só depois retira a configuração antiga `npm:opencode-ai`.
Mantém a instalação anterior para recuperação (`--no-prune`), preserva dados e
configurações do aplicativo e salva o config mise anterior em
`~/.local/state/gran/opencode-backups`. Atualiza também o atualizador, o menu de
instalação e o doctor do Gran para usar/verificar o novo caminho.

Novas instalações e `gran update` usam o mesmo mecanismo. O doctor agora testa
a execução do OpenCode, além de localizar o comando. A instalação npm anterior
podia deixar apenas o lançador: por padrão o mise não executa scripts de builds
desses pacotes, conforme a [documentação npm do mise](https://mise.jdx.dev/dev-tools/backends/npm).

O OpenCode já faz parte da instalação normal: a etapa de ferramentas instala
o release oficial, prepara os shims e executa o comando comum `opencode --version`.
Se o binário ou a resolução do comando falhar, a instalação interrompe nessa
etapa. Não é necessário executar um reparo manual após uma instalação nova.

## Aliases e atalhos do notebook

A instalação inclui `gran-aliases.fish` e suas ferramentas eza, fzf, bat, zoxide,
tmux, neovim, openssh e file. `lt` usa árvore até o segundo nível com detalhes,
ícones e Git; `lta` inclui também os ocultos. Abra um terminal fish novo após
a atualização. Os aliases de ferramentas opcionais continuam requerendo seus
respectivos aplicativos.

| Atalho | Comportamento atual |
| --- | --- |
| Ctrl+Super+Alt+T | btop no Kitty, flutuante e centralizado, 875×600 |
| Super+Enter / Super+Shift+T | Terminal padrão |
| Super+Shift+O | Abrir ou focar OpenCode |
| Super+Alt+Enter | Abrir ou focar Codex |
| Ctrl+Super+Enter | Abrir ou focar TUIOS, quando instalado |
| Super+D / Super+Shift+F | Files com o wrapper atual |
| Super+S | Console do agente, iniciando o agente se estiver vazio |
| Super+Q | Fechar janela; Super+W fica livre para o aplicativo |

Todos os nove arquivos de atalhos pessoais/defaults são exportados em overlay;
a procedência e os hashes ficam em `manifests/shortcuts.json`. Também são
incluídos o console, os lançadores TUI, as regras de janela e o tema/configuração
do btop. `scripts/update-desktop.sh` aplica o conjunto com backup. Essa atualização
substitui os atalhos do destino pelos atuais deste notebook, conforme solicitado.
