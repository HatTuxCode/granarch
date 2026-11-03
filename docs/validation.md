# Validação e recuperação

Verificações locais sem instalar no computador:

```bash
bash install.sh --verify
python -m unittest discover -s tests -v
bash -n install.sh
```

Os testes usam diretórios temporários para aplicar o home e preparar um sistema
fictício. Verificam a herança integral dos módulos de atalhos, backups e
reaplicação, CLI Gran/skills, ausência de chaves/repos, nome da fonte portada,
SHA-256 do Zen e rejeição de caminhos externos em archives.

A camada de boot é testada com configurações fictícias, preservando os
identificadores e hooks de criptografia do destino. A paleta é gerada em um
home temporário. Essas verificações não substituem o teste em VM.

Validação completa em Arch x86_64:

1. Instalar a base com LUKS, bootloader, usuário e sudo.
2. Aplicar GranArch e conferir backups antes de reiniciar.
3. Verificar o boot silencioso, unlock Plymouth, autologin SDDM e tema.
4. Executar gran doctor e hyprctl configerrors.
5. Conferir barra, wallpaper, menus, todos os atalhos e seus apps opcionais.
6. Testar Kitty/fish/cursor trail, cores GTK3/GTK4/Qt e primeiro uso do Zen.
7. Testar Codex, OpenCode e a descoberta das três skills.
8. Testar áudio, compartilhamento de tela, lock por senha, tampa e suspensão.
9. No notebook real, conferir Fn Lock, luz do teclado, carga95%, transições
   AC/bateria e o limite de 25% para a tela.
10. Testar atualização em snapshot de VM antes da instalação definitiva.

Logs: journalctl --user -b -t gran-shell, journalctl -b -u sddm e os logs do
mkinitcpio. Não publique logs, core dumps ou dados de conta automaticamente.

Backups de arquivos de usuário ficam em ~/.local/state/gran/backups,
install-backups e theme-backups. Os do sistema ficam em /var/backups/gran.
Consulte changes.json; restaure apenas os arquivos desejados. Arquivos novos
não têm cópia anterior e precisam ser removidos ao desfazer.

O backup do instalador guarda o shell anterior e os links do display manager
e do target padrão. Restaurar esses arquivos e o initramfs exige revisar o
estado do destino; não há rollback automático de pacotes ou de boot.
Não restaure arquivos de discos, EFI ou criptografia de outra máquina.

## Preparação CachyOS — 02/11/2026

- 22 testes locais passam, incluindo HOME vazio, pacotes ausentes, Hyprland
  incompatível e preservação do boot gerenciado do CachyOS.
- Os 97 pacotes do manifesto foram encontrados nas bases locais do pacman;
  isso não comprova a disponibilidade de cada variante no espelho CachyOS.
  `bash install.sh --check` fará essa conferência no destino.
- Snapshot validado por SHA-256 e sintaxe Bash conferida.
- VM preparada com `cachyos-desktop-linux-260809.iso`, UEFI, 3 GiB de RAM,
  2 CPUs, disco esparso próprio de 64 GiB e CD GranArch com checksum.
- XML da VM validado pelo schema libvirt; `qemu-img check` sem erros;
  conteúdo e rótulo do CD GranArch conferidos.

Este ambiente não possui `/dev/kvm`; a VM não foi iniciada pelo agente.
A instalação mínima será feita pelo usuário. Ainda faltam a execução real
completa do pós-instalador, o download/compilação upstream no destino e a
validação da sessão gráfica. No CachyOS, o boot nativo é preservado por padrão;
o teste não exige o Plymouth Gran.

## Preparação EndeavourOS — 02/11/2026

O destino atual substitui o teste CachyOS por EndeavourOS mínimo. O instalador
detecta `ID=endeavouros`, preserva dracut/kernel-install e exclui mkinitcpio e
Plymouth da transação. O modo `--boot` é recusado nesse destino. Os testes
cobrem os padrões por distribuição, a filtragem dos pacotes e a preservação
dos arquivos de dracut, kernel command line e entradas de boot.

A nova VM tem disco e NVRAM novos em `vm/endeavouros/`, nome
`granarch-endeavouros` e usa `EndeavourOS_Titan-Nova-2026.08.15.iso`. Mantém
UEFI, 3 GiB de RAM, 2 CPUs e disco esparso de 64 GiB. O CD GranArch contém
o pacote atualizado e seu SHA-256.

O disco CachyOS antigo estava aberto e o acesso ao socket libvirt do host foi
negado pelo sandbox. Por isso, sua remoção é concluída pelo comando
`bash scripts/vm.sh replace-cachyos` no terminal do notebook: ele verifica
identidade/UUID, encerra somente a VM antiga, remove sua definição e seus
arquivos e abre o EndeavourOS. Essa limpeza tem testes com comandos libvirt
simulados, cobrindo UUID diferente, conexão indisponível e disco ocupado.

A execução real do pós-instalador e a sessão gráfica no EndeavourOS continuam
pendentes da instalação mínima pelo usuário.

## Paridade visual com o desktop — 02/11/2026

As seguintes peças foram copiadas da instalação Gran em uso para `overlay/`,
sem recapturar o snapshot antigo: símbolo G da barra, arte do terminal,
configuração fastfetch, lançador Sobre e CSS `gran-nautilus-blur.css`. Seus
bytes foram comparados com os arquivos locais carregados. O fastfetch local
carregou a configuração sem erros.

O Zen de referência é 1.24b. A configuração exporta somente três preferências
visuais: tema da barra, modo compacto ao iniciar e habilitação do CSS do perfil.
Nenhum prefs.js, perfil, conta, cookie, favorito, workspace ou histórico do
notebook é incluído. Ícones são extraídos do próprio download upstream e
instalados em hicolor; o lançador usa o caminho do ícone para evitar ambiguidades
do tema de ícones. Instalar novamente a mesma versão também repara a integração.

O tema do Files é gerado mesmo antes de existir um perfil Zen. O import de fosco
fica após os imports da paleta e o lançador Files usa nautilus-remember para
aplicar o mesmo tratamento de protocolo gráfico que o atalho atual.

`update-desktop.sh` atualiza instalações já existentes com backup, sem reaplicar
atalhos/monitores ou baixar/downgradear o navegador. Os testes usam perfis e
bancos de dados fictícios, isolam dconf da sessão real e verificam primeiro uso,
reparo do ícone sem download, reaplicação e preservação dos dados pessoais.

35 testes passam; arquivos .desktop e scripts Bash foram validados. O visual
real do EndeavourOS ainda deve ser conferido após publicar/aplicar e reentrar
na sessão. Este ambiente continua sem acesso de rede ao GitHub para o push.

## OpenCode sem postinstall — 02/11/2026

A instalação npm podia concluir sem preparar o binário OpenCode. A entrega foi
alterada para `aqua:anomalyco/opencode`, explicitamente pelo release oficial.
Instalação inicial, catálogo opcional e atualização passam pelo mesmo helper.
Ele exige que `opencode --version` rode antes de retirar a configuração npm
anterior. `gran doctor` também executa a verificação, em vez de apenas localizar
o comando. Codex continua em seu fluxo npm existente.

`repair-opencode.sh` salva a configuração mise e os componentes Gran afetados,
preserva a instalação npm anterior com `--no-prune` e atualiza o runtime após
o teste do binário. Não acessa nem substitui contas/configurações do OpenCode.
Os testes simulam download com erro, executável com erro e migração bem-sucedida,
verificando preservação dos dados e do runtime anterior em caso de falha.

38 testes locais passam. A remoção de um pedido npm inexistente com `--no-prune`
foi conferida com o mise real em HOME temporário. O download/execução do release
real no EndeavourOS precisa ser validado pelo usuário: a rede deste ambiente
continua sem acesso ao GitHub.

## Barra nativa e verificação automática do OpenCode — 02/11/2026

A aplicação inicial do home agora seleciona `gran.bar`. O overlay inclui os
29 arquivos da barra nativa em uso, comparados byte a byte com o runtime local:
6 px de margem lateral, 3 px no topo e raio `Style.cornerRadius`, ligado ao
arredondamento Hyprland (4 px no perfil atual). Os 16 arquivos QML foram
analisados pelo qmlformat sem erros de sintaxe. O snapshot antigo e sua cópia
`hattux.bar` são preservados como referência; a instalação ativa a barra nativa.

A atualização de aparência migra somente o ID antigo da barra no shell.json,
com backup e preservação de layout, plugins e demais preferências. Também
passa a incluir a correção do OpenCode no fluxo único de update-desktop.sh.

A etapa 3 de install.sh usa install-tools.sh e interrompe se falhar o teste do
binário oficial OU o comando comum `opencode --version`. Os testes executam a
etapa real com backends simulados, incluindo o caso em que `mise exec` funciona
mas o comando do usuário falha. O primeiro uso normal fica como condição de
sucesso da instalação, em vez de depender de reparo manual posterior.

42 testes passam, incluindo instalação nova da barra, migração preservando o
layout e falhas nos dois caminhos de execução do OpenCode. Isso não substitui
a conferência visual do EndeavourOS nem o download real do OpenCode no destino.

## Aliases fish, atalhos atuais e btop — 02/11/2026

A configuração corrente tinha alterações posteriores à captura original:
terminal em Super+Shift+T, Codex em Super+Alt+Enter, TUIOS em Ctrl+Super+Enter,
Super+W liberado e inicialização do agente pelo console. Foram exportados os
nove arquivos de atalhos e o qconsole correspondente, com hashes de origem e
exportação em manifests/shortcuts.json. Nenhum caminho do usuário de origem é
mantido; apply-home e apply-shortcuts substituem o marcador pelo HOME do destino.

O arquivo gran-aliases.fish foi exportado sem fish_variables nem histórico,
junto das dependências eza/fzf/bat/zoxide/tmux/neovim/openssh/file. A inicialização
interativa do zoxide é configurada no fragmento fish do Gran. O doctor verifica
as ferramentas e a existência de lt/lta dentro do fish.

Os testes executam lt/lta no fish com eza real, carregam todos os módulos de
atalhos em Lua com a API do compositor simulada e verificam a resolução final
das combinações depois dos overrides. O teste do btop percorre o lançador real
até um terminal/uwsm simulado e verifica a classe org.gran.btop, a seleção do
Kitty, o tema e as regras de janela flutuante/centralizada 875×600. A atualização
preserva monitores e dados de conta e guarda os atalhos anteriores em backup.

46 testes passam. luac/fish validaram a sintaxe; os oito novos pacotes foram
encontrados nas bases locais do pacman. A consulta hyprctl binds da sessão do
notebook não foi possível (socket indisponível no ambiente do agente), então a
paridade foi conferida nos arquivos efetivamente carregados. O teste final de
teclado e janelas no EndeavourOS exige aplicar a atualização e reentrar na sessão.
