-- Keep only your personal input overrides here. Uncommented settings below
-- replace Gran's defaults.

-- Keyboard layout and options.
-- See https://wiki.hypr.land/Configuring/Basics/Variables/#input
hl.config({
  input = {
    -- Remover compose:caps para que Caps Lock funcione normalmente
    -- (sem essa opção, Caps Lock volta a ser Caps Lock)
    kb_options = "shift:both_capslock_cancel",
    touchpad = {
      natural_scroll = true,
      drag_3fg = true,
    },
  },
})

-- Touchpad: aumento de sensibilidade de 0 para 0.15.
hl.device({
  name = "asue140a:00-04f3:3134-touchpad",
  sensitivity = 0.15,
})

-- App-specific touchpad scroll speeds.
-- o.window("(Alacritty|kitty|foot)", { scroll_touchpad = 1.5 })
-- o.window("com.mitchellh.ghostty", { scroll_touchpad = 0.2 })

-- Enable touchpad gestures for changing workspaces.
-- See https://wiki.hypr.land/Configuring/Advanced-and-Cool/Gestures/
-- hl.gesture({ fingers = 3, direction = "horizontal", action = "workspace" })

-- Enable touchpad gestures for moving focus (helpful on scrolling layout).
-- hl.gesture({ fingers = 3, direction = "left", action = function() hl.dispatch(hl.dsp.focus({ direction = "l" })) end })
-- hl.gesture({ fingers = 3, direction = "right", action = function() hl.dispatch(hl.dsp.focus({ direction = "r" })) end })

-- Fathom: quatro dedos para cima abre; para baixo fecha a visão geral.
-- Workspaces: quatro dedos para a direita vai à esquerda, e vice-versa.
hl.config({ gestures = { workspace_swipe_invert = true } })
hl.gesture({ fingers = 4, direction = "horizontal", action = "workspace" })

hl.gesture({
  fingers = 4,
  direction = "up",
  action = function() hl.exec_cmd("gran-shell fathom open") end,
})
hl.gesture({
  fingers = 4,
  direction = "down",
  action = function() hl.exec_cmd("gran-shell fathom cancel") end,
})
