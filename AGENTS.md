# GranArch
Responda em português. Este projeto instala Arch Linux puro x86_64 com Hyprland
Lua e Noctalia nativo v5. A instalação Fedora da máquina é apenas referência.
Não execute o instalador nesta máquina e não altere seu desktop durante o desenvolvimento.

Preferências do destino: preservar atalhos, programas, paleta, efeitos e a barra
capturados da máquina; monitor 125%; família padrão sans-serif do Noctalia,
fonte base lógica 11 px (escala 11/14), preservando tamanhos relativos.
Não importar ajustes pessoais de fontes/tamanhos (9,9 pt, fontconfig, GTK, Qt,
Kitty ou CSS do Zen); usar os padrões dos aplicativos. Não achatar a hierarquia
de títulos/texto pequeno/grande do Noctalia.
Dolphin usa pastas KDE Breeze com desenho e cores originais.
GranBreezeContrast altera somente ícones de ações para contraste; cursor breeze_cursors.
Não instalar Yaru nem gerar GranToolbar. Codex/OpenCode via mise aqua.
Layouts somente dwindle e scrolling, mantendo o workspace vazio extra.

Payload usa allowlist, caminhos @HOME@ substituídos na aplicação; nunca copiar
credenciais, perfis de navegador, Wi-Fi, históricos ou IDs de disco da origem.
Backups de destino em ~/.local/state/gran/backups/. Histórico anterior preservado
na branch archive/before-native-arch-*. Não reintroduzir o Quickshell antigo.

Verificação: python3 scripts/verify.py e python3 -m unittest discover -s tests -v.
Mudanças de boot, hardware e aparência precisam também de teste real em VM/Arch;
validação local no Fedora não prova instalação nem boot.

Calamares: senha mínima de 2 caracteres. Janela deve caber na área útil, com
escala adaptativa apenas do instalador; preservar fontes e escala do desktop.
Não reiniciar o instalador durante uma instalação em andamento para aplicar ajustes.

Antes de novos envios ao GitHub, testar as correções na VM até concluir a
instalação e validar o boot. Manter as correções locais durante esse ciclo.

Navegadores: Chromium oficial Arch com flags Wayland/libsecret e políticas de cor;
Zen como pacote zen-browser-bin (receita AUR revisada), sem instalação portátil.
Paleta Noctalia exporta CSS central do Zen via AutoConfig, sem copiar perfis.
Dolphin/Qt/GTK usam GranBreezeContrast; não reativar o template Qt do Noctalia
em paralelo ao gerador Gran. Não recolorir pastas.
Incluir Ark, 7zip/unrar e ações nativas Extrair aqui/Extrair para; Discos do GNOME,
DiskTree e Evince. Não instalar GranControl na ISO nem manter seu atalho nela.
Os testes visuais na VM são feitos pelo usuário; fornecer roteiro curto e não
executar testes automáticos ou publicar alterações antes da validação dele.

Login SDDM usa o tema gran da máquina de origem, com sessão granarch.desktop
e fallback para o primeiro usuário comum no primeiro login. Noctalia continua
responsável pelo bloqueio dentro da sessão; não trocar os dois componentes.

Preferência atualizada: pastas do Dolphin com desenho e cores Breeze originais.
Não recolorir pastas. GranBreezeContrast sobrescreve somente ícones de ações
para contraste na barra/menus e herda todas as pastas diretamente do Breeze.
