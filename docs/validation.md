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
