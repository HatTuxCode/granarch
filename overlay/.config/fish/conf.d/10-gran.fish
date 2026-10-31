set -gx GRAN_PATH $HOME/.local/share/gran
fish_add_path --prepend $HOME/.local/bin $HOME/.local/share/mise/shims $GRAN_PATH/bin
set -gx TERMINAL kitty
set -gx QT_QPA_PLATFORMTHEME gtk3
set -gx QT_STYLE_OVERRIDE Fusion
set -gx QT_QUICK_CONTROLS_STYLE Fusion
if status is-interactive; and command -q mise
    mise activate fish | source
end
