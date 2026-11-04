if [ -d "$HOME/.local/share/gran" ]; then
 export GRAN_PATH="$HOME/.local/share/gran"
 export PATH="$HOME/.local/share/mise/shims:$HOME/.local/bin:$GRAN_PATH/bin:$PATH"
 export TERMINAL=kitty QT_QPA_PLATFORMTHEME=qt6ct QT_STYLE_OVERRIDE=Fusion QT_QUICK_CONTROLS_STYLE=Fusion
fi
