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
