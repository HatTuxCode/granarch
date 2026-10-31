# Lançador e menu Gran

O lançador utiliza o mesmo AppGrid/AppLibrary Quickshell da origem: pesquisa
digitando, navegação por teclado, grade de aplicativos, interação com o dock e
leitura dos arquivos .desktop instalados. Os atalhos originais continuam:
Super+Space para o menu e Super+Alt+Space para Apps. Também é possível abrir
com `gran launch apps`.

O menu expandido contém Apps, Learn, Appearance, Trigger, Setup, Install,
Remove, Update, About e System. A definição fica em
`$GRAN_PATH/default/gran/gran-menu.jsonc` e as extensões pessoais em
`~/.config/gran/extensions/gran-menu.jsonc`.

Appearance mantém os controles herdados para barra, relógio, posição, fundo,
janelas, gaps, opacidade, cantos, animações, layouts e dock. Trigger mantém as
ações compatíveis de captura, hardware, lembretes e testes. Recursos opcionais
dependem de suas ferramentas, como na origem.

## Instalar e remover

- **Package:** busca pacotes dos repositórios configurados, mostra informações
  e usa a transação normal do pacman com confirmação. A instalação usa uma
  atualização completa para evitar uma atualização parcial de bibliotecas.
- **Web App:** solicita nome, URL e navegador. Chromium abre a janela de app,
  com perfil próprio e é instalado somente se você escolher esse modo e ele
  ainda não estiver disponível. A opção Zen abre uma janela normal do Zen.
  Isso não muda seu navegador padrão.
- **AUR:** opcional. Se yay não existir, oferece compilar a receita do AUR,
  exibindo o PKGBUILD antes. Não adiciona repositórios binários ou mirrors.
- **Browser, Terminal, Editor, Development, Services, Fonts, Gaming e AI:**
  catálogo opcional. Nada desse catálogo é instalado por abrir o menu.
  Ferramentas de desenvolvimento/IAs usam mise; os demais itens usam suas
  fontes declaradas. Steam só aparece na árvore quando multilib está habilitado.

Os Web Apps criam entradas .desktop no home e aparecem no lançador. Remover
um Web App pelo menu ou pelo lançador retira o atalho e o registro, mantendo
seu perfil de navegador. Os arquivos removidos ficam no backup de Web Apps.

## Setup

Inclui monitores, atalhos, input, layout de teclado, idioma da interface,
rede/Wi-Fi, DNS, QR de Wi-Fi, padrões de navegador/terminal/editor/agente,
plugins, configuração Git, fuso horário, senha, cadastro de digital, servidor
SSH, impressoras, energia do notebook, Kitty, fish e sincronização das cores.

O idioma do shell muda com os catálogos existentes. O LANG dos aplicativos
só acompanha automaticamente se o locale correspondente já estiver gerado.
O cadastro de digital não troca silenciosamente a configuração PAM.
As alterações em arquivos existentes por Setup recebem backup.

Os fluxos específicos da distribuição de origem — canais stable/edge,
preinstalls e factory reset — não fazem parte do Gran. O boot e as políticas
do notebook são configurados pelo pós-instalador próprio.

Comandos equivalentes:

```fish
gran launch apps
gran menu summon install
gran menu summon setup
gran pkg install
gran pkg remove
gran webapp install
gran webapp list
gran webapp remove
gran install browser firefox
gran install development python
gran setup default-agent
gran setup keyboard
```

O catálogo está em `manifests/optional-apps.json`. O menu pode ser regenerado
na máquina de origem com `python scripts/build-menu.py`, que reaproveita apenas
as ações compatíveis e acrescenta os fluxos nativos do Gran.
