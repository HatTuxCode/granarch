-- Change the default Gran look'n'feel.

hl.config({
  general = {
    -- O Hyprland aplica gaps_in dos DOIS lados do vao entre duas janelas. A
    -- borda de 2px (bloco lacquer mais abaixo) fica DENTRO da caixa da janela,
    -- entao ela nao come a fresta de wallpaper: o que se ve entre duas janelas
    -- e 2*gaps_in, e na borda da tela e gaps_out. Para o mesmo espacamento nos
    -- dois lugares, gaps_in = gaps_out / 2.
    gaps_in = 3,
    gaps_out = 6,
  },
})

-- Sombra nas janelas, com os valores padrao do Hyprland.
hl.config({
  decoration = {
    shadow = {
      enabled = true,
      range = 4,
      render_power = 3,
      color = "rgba(1a1a1aee)",
    },
  },
})

-- https://wiki.hypr.land/Configuring/Basics/Variables/#decoration
-- hl.config({
--   decoration = {
--     -- Use round window corners.
--     rounding = 8,
--
--     -- Dim unfocused windows (0.0 = no dim, 1.0 = fully dimmed).
--     dim_inactive = true,
--     dim_strength = 0.15,
--   },
-- })

-- https://wiki.hypr.land/Configuring/Basics/Variables/#animations
-- hl.config({
--   animations = {
--     -- Disable all animations.
--     enabled = false,
--   },
-- })

-- https://wiki.hypr.land/Configuring/Basics/Variables/#layout
-- hl.config({
--   layout = {
--     -- Avoid overly wide single-window layouts on wide screens.
--     single_window_aspect_ratio = { 1, 1 },
--   },
-- })

-- https://wiki.hypr.land/Configuring/Layouts/Scrolling-Layout/
-- hl.config({
--   scrolling = {
--     -- See only one column per screen instead of two.
--     column_width = 0.97,
--   },
-- })

-- >>> omaland managed block >>>
-- Written by Omaland. Safe to hand-edit: Omaland re-reads this block
-- every time it opens, and only ever rewrites what's between the fences.
hl.config({
  decoration = {
    rounding = 5,

    blur = {
      enabled = true,
    },
  },
})
-- <<< omaland managed block <<<

-- Blur da barra: ela e um layer shell (namespace gran-bar), nao uma janela,
-- entao nao pega o decoration.blur das janelas. O alpha de 90% fica em
-- ~/.config/gran/shell.toml ([bar] background-alpha).
hl.layer_rule({ match = { namespace = "^gran-bar$" }, blur = true })

-- Vidro (frosted glass) nas janelas sem foco.
-- Fica DEPOIS do bloco do Omaland: o Omaland reescreve o bloco acima e
-- desligaria o blur de novo.
--
-- O wallpaper precisa ter detalhe pra ter algo que borrar. Se voce pre-borrar a
-- imagem, o vidro some: sobra uma cor chapada e a janela parece so
-- "transparente". Por isso o wallpaper fica nitido e quem borra e o compositor.

-- >>> lacquer managed block >>>
-- Written by Lacquer. Safe to hand-edit: Lacquer re-reads this block
-- every time it opens, and only ever rewrites what's between the fences.
hl.config({
  cursor = {
    hide_on_key_press = true,
    warp_on_change_workspace = 1,
  },

  decoration = {
    dim_inactive = true,
    rounding = 4,
    rounding_power = 2,

    blur = {
      enabled = true,
      size = 14,
      passes = 2,
      noise = 0.0117,
      contrast = 0.8916,
      brightness = 1.0,
      vibrancy = 0.1696,
      vibrancy_darkness = 0.0,
      new_optimizations = true,
      popups = true,
      special = true,
      xray = false,
    },

    glow = {
      enabled = false,
      range = 12,
    },

    shadow = {
      enabled = false,
      range = 16,
      render_power = 2,
      scale = 1,
      sharp = false,
    },
  },

  general = {
    border_size = 2,
  },
})

hl.animation({ leaf = "borderangle", enabled = false })
-- <<< lacquer managed block <<<

-- Opt another application in to Gran's standard transparency.
-- Find its class with: hyprctl clients
-- o.transparent_window("my-app")
-- o.transparent_window("my-app", "0.9 0.85") -- Custom active/inactive opacity.
