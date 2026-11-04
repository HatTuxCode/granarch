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
Dolphin usa desenho original KDE Breeze, com pastas verde-cinza Nord #8fa89b
(tema herdado GranBreezeNord); demais ícones Breeze. Cursor breeze_cursors.
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
