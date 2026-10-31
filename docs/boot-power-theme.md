# Boot, energia e cores

O estado capturado utiliza Limine, Plymouth com Nord e SDDM com entrada
automática. O pós-instalador porta os assets atuais de Plymouth/SDDM para Gran,
e o lockscreen da sessão usa o mesmo wallpaper e os tokens Nord do shell.

O script oculta o menu do bootloader existente e adiciona os parâmetros de
boot silencioso. Não registra uma nova entrada EFI nem altera as partições.
O initramfs mantém seus hooks de armazenamento, criptografia e resume.
Plymouth é inserido depois de systemd/udev e antes do desbloqueio por
encrypt/sd-encrypt. O mkinitcpio é regenerado no próprio destino.

O SDDM usa o greeter Wayland com Hyprland e a sessão Gran/UWSM. O autologin só
ocorre no boot; depois de um logout explícito o greeter permanece disponível.
A senha do lockscreen da sessão continua validada por PAM. O monitor de
suspensão usa um inibidor de atraso para tentar confirmar o bloqueio seguro
antes de liberar a suspensão. O timeout de inibição é 15s, como na origem.

## Padrões do notebook

| Situação | Política |
|---|---|
| Na tomada | performance; sem apagar automaticamente a tela |
| Bateria acima de 25% | balanced; sem apagar automaticamente a tela |
| Bateria até 25% | power-saver; tela apaga após 20min ociosa |
| Luz do teclado | apaga após 30s ociosa na bateria; volta com atividade |
| Carga máxima | 95%, reaplicada no boot e em eventos de alimentação |
| Tampa | bloqueia ao fechar; reconcilia monitores e acorda ao abrir |
| Suspensão | bloquear antes de suspender |
| Idle lock normal | desabilitado pelo perfil personalizado; valor configurado 1800s preservado |
| Backlight inicial | nível 1, preservado e atualizado por mudanças manuais |

O estado ASUS observado foi `fnlock_default=N`; essa configuração é
preservada em `manifests/notebook.json`. `Y` força o estado alternativo do
módulo. A correspondência com teclas multimídia/F1..F12 deve ser conferida no
hardware, porque o firmware também participa desse comportamento.

ASUS recebe asusctl de extra e sua configuração atual: carga 95%, perfil
Performance na tomada e Quiet na bateria, com vinculação de EPP. Intel recebe
thermald de extra. O controle de perfis de energia continua no
power-profiles-daemon oficial, com política de adaptação por usuário a cada
minuto. Em outro hardware, o perfil cai para balanced quando performance não
é oferecido e os recursos inexistentes são ignorados.

No Quickshell upstream, a porcentagem UPower é uma fração 0..1; a comparação
foi normalizada para 0..100 antes de aplicar o limite 25%.

## Cores dos aplicativos

`gran theme sync` gera CSS de GTK3 e GTK4/libadwaita a partir de
`~/.local/state/gran/current/theme/colors.toml`. Os arquivos são importados
pelos estilos globais do usuário, preservando CSS que ele já tinha.

Qt usa a integração de paleta GTK3 e o estilo Fusion; Qt Quick Controls usa
Fusion com a paleta de sistema. Kitty inclui o tema resolvido e mantém o
efeito de cursor e todos os ajustes do arquivo de origem. Aplicativos de
terminal herdam suas cores pelo terminal.

O Zen novo usa um perfil Gran sem dados de conta, com CSS gerado antes do
primeiro uso. A integração também atende os perfis existentes em .config/zen
e .zen. Websites e documentos não são recoloridos.

Apps com interface própria, estilos embutidos, Wine ou sandbox podem ignorar
as preferências globais. Trate esses casos com integração individual, sem
prometer que qualquer aplicativo arbitrário obedecerá aos tokens do desktop.

Referências:
[hooks Plymouth](https://wiki.archlinux.org/title/Plymouth?useskinversion=1),
[SDDM](https://github.com/sddm/sddm/blob/develop/data/man/sddm.conf.rst.in),
[Fusion](https://doc.qt.io/qt-6.10/qtquickcontrols-fusion.html),
[libadwaita](https://gnome.pages.gitlab.gnome.org/libadwaita/doc/1.6/css-variables.html).
