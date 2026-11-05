# Teste manual na VM

As alterações ainda não foram enviadas ao GitHub. O teste visual é feito pelo usuário.

1. Feche Zen, Chromium e Dolphin. Extraia o pacote local da atualização e execute
   `bash scripts/update-installed.sh` como usuário comum. A senha administrativa
   é solicitada no terminal. Não envie senha ou token no chat.
2. No launcher, abra Zen e Chromium. Confira barras, menus e painéis na paleta
   Nord. No Chromium, `chrome://policy` deve mostrar BrowserThemeColor e
   BrowserColorScheme sem erro. Use “Recarregar políticas” se necessário.
3. Troque a paleta pelo Noctalia. Confira que os aplicativos acompanham as cores;
   o Zen recebe a folha central automaticamente. Para o primeiro teste, reinicie
   ambos os navegadores após a atualização. Sites e documentos mantêm suas cores.
4. Abra Dolphin: conferir fundo, menus e barra no mesmo estilo da origem, com
   ícones Breeze de pastas com as cores originais, sem recoloração e sem Yaru.
   Conferir também os ícones claros da barra e dos menus.
5. Em uma pasta temporária, crie um ZIP com um arquivo de teste. Pelo botão
   direito, conferir “Extrair aqui” e “Extrair para…” e abrir o resultado.
6. Abrir Discos, DiskTree e um PDF no Evince. No DiskTree, apenas abrir/visualizar;
   não é necessário apagar arquivos. Verificar que GranControl saiu do launcher.
7. Enviar capturas dos aplicativos e qualquer mensagem de erro. Só depois da
   validação enviar ao GitHub e gerar uma nova ISO.

Para o ajuste pontual de cores após a primeira atualização, usar
`bash scripts/fix-app-colors.sh`; não precisa reconstruir os pacotes. Fechar o
Dolphin com Ctrl+Q e o Zen pelo menu Sair antes de reabrir. No Zen, a preferência
`gran.theme.status` em about:config deve ser `loaded`; um valor de erro ou ausência
dessa preferência identifica falha de carregamento, em vez de confundir arquivo
gerado com aparência aplicada.

O login SDDM usa o tema gran da máquina de origem. O ajuste é aplicado no
próximo login; não reiniciar o SDDM para testar durante a sessão. O bloqueio
Super+Ctrl+L continua sendo o Noctalia e é um componente diferente.
