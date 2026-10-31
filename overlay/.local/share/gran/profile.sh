# Gran login environment. UWSM and fish have matching user fragments.
if [ -d "$HOME/.local/share/gran" ]; then
  export GRAN_PATH="$HOME/.local/share/gran"
  export PATH="$HOME/.local/bin:$HOME/.local/share/mise/shims:$GRAN_PATH/bin:$PATH"
  export QT_QPA_PLATFORMTHEME=gtk3
  export QT_STYLE_OVERRIDE=Fusion
  export QT_QUICK_CONTROLS_STYLE=Fusion
fi
