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
