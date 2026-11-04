set -gx GRAN_PATH $HOME/.local/share/gran
fish_add_path --prepend $HOME/.local/share/mise/shims $HOME/.local/bin $GRAN_PATH/bin
set -gx TERMINAL kitty
set -gx QT_QPA_PLATFORMTHEME qt6ct
set -gx QT_STYLE_OVERRIDE Fusion
set -gx QT_QUICK_CONTROLS_STYLE Fusion

if status is-interactive; and command -q mise
    mise activate fish | source
end

set -gx EDITOR nvim
if status is-interactive
    mkdir -p $HOME/.cache/opencode-tmp
    if command -q zoxide
        zoxide init fish | source
    end
end
