# Roteiro de validação

1. No Fedora de desenvolvimento: `./install.sh --verify` e unittest; não instalar.
2. No Arch de build: compilar Calamares, gerar ISO e conferir SHA-256.
3. VM UEFI/OVMF com disco descartável: iniciar ISO, conferir sessão live e abrir
   Calamares pelo launcher; verificar rede antes de prosseguir.
4. Calamares: testar ext4 sem criptografia, depois instalação criptografada em
   outra VM; conferir idioma pt_BR, ABNT2, usuário comum, senha e revisão do disco.
5. Reiniciar sem a ISO; selecionar GranArch. Validar boot, cofre, Noctalia,
   atalhos, fontes 11 px e escala 125%; comparar barra e aparência com a referência.
6. `gran doctor`, `gran update`, abrir Zen/Chromium/Dolphin, imagem, virt-manager,
   Docker e os dois agentes. Conferir os ícones Breeze verde-cinza e a troca de
   tema sem restaurar Yaru. Conferir Print, clipboard e workspaces.
7. No ASUS: observar iwlwifi, Bluetooth, i915, áudio SOF, leitor SD, NVMe/VMD,
   Fn, drag_3fg, energia AC/bateria, limite de carga, tampa, suspensão/retomada.
   VM não comprova esses recursos físicos.

Ainda não executado: compilação do Calamares no Arch, geração/boot da ISO e
instalação completa. Os testes locais não removem essa pendência.

## Ciclo real de teste em 04/11/2026

A ISO iniciou na VM BIOS/QEMU com vídeo Virtio. Foram identificados e corrigidos
na sessão live: espera circular na inicialização, permissões de execução do
payload e apresentação obrigatória do Calamares. Hyprland, Noctalia e o
assistente abriram. Instalação online instalou pacotes e criou o usuário.

A etapa de desktop expôs falhas que os testes de sintaxe não cobriam: leitura de
`noctalia v5.4.1`, criação do cache do usuário como root e validação do Hyprland
sem XDG_RUNTIME_DIR em chroot. O staging agora fica em /opt; a validação usa um
runtime temporário isolado. Correções recentes permanecem locais até o fim do
teste de instalação e boot. A VM não substitui testes físicos de Fn e energia.
