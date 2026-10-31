-- Keep only your personal keybinding overrides here. Add new bindings or
-- unbind defaults before replacing them.

-- See current bindings and descriptions:
--   gran menu keybindings --print

-- To disable every Gran default binding, set this in
-- ~/.config/hypr/hyprland.lua before require("default.hypr.gran"), then add
-- only the bindings you want below:
--   gran_default_bindings = false

-- To disable all preinstalled app/webapp bindings, set:
--   gran_preinstalled_bindings = false

-- Add a new binding.
-- o.bind("SUPER + SHIFT + R", "SSH", "alacritty -e ssh your-server")

-- Change an existing binding by unbinding it first, then binding the key again.
-- This example changes SUPER+SPACE from the launcher to the Gran root menu.
-- hl.unbind("SUPER + SPACE")
-- o.bind("SUPER + SPACE", "Gran menu", "gran-menu toggle root")

-- Disable a default binding without replacing it.
-- hl.unbind("SUPER + SHIFT + B")

-- File manager: SUPER + D (was SUPER + F)
hl.unbind("SUPER + SHIFT + F")
hl.unbind("SUPER + D")
o.rebind("SUPER + D", "File manager", { launch = "@@GRAN_HOME@@/.local/bin/nautilus-remember --new-window" })

-- Full screen: SUPER + F (Gran default, already bound by tiling.lua)

-- Full width (maximize): SUPER + ALT + M (was SUPER + ALT + F)
hl.unbind("SUPER + ALT + F")
o.bind("SUPER + ALT + M", "Full width", hl.dsp.window.fullscreen({ mode = "maximized" }))

-- Pop window out (float, center & pin) with smaller dimensions (was 1300x900)
o.rebind("SUPER + O", "Pop window out (float & pin)", "gran-hyprland-window-pop 1000 650")

-- Stash window: SUPER + ALT + H. Stashes the focused window; press again to
-- bring it back to its original workspace, even from another workspace.
local stashed_window = nil

local function stash_restore()
  if not stashed_window then
    return
  end

  stashed_window = nil

  -- Bring the window back to the workspace the user is on now, not the one it
  -- left from.
  local current = hl.get_active_workspace()
  if current and current.id then
    hl.dispatch(hl.dsp.focus({ workspace = "special:stash" }))
    hl.dispatch(hl.dsp.window.move({ workspace = current.id, follow = true }))
  end
end

local function stash_away()
  local active = hl.get_active_window()
  if not active or not active.address or not active.mapped or active.hidden then
    return
  end

  stashed_window = { address = active.address, workspace = active.workspace and active.workspace.id }
  hl.dispatch(hl.dsp.window.move({ workspace = "special:stash", follow = false }))
end

o.bind("SUPER + ALT + H", "Stash window", function()
  if stashed_window then
    stash_restore()
  else
    stash_away()
  end
end)

-- Terminal: SUPER + ENTER opens the Gran default terminal
hl.unbind("SUPER + RETURN")
o.bind("SUPER + RETURN", "Terminal", { gran = "terminal" })

-- Night light with weaker tint (~30%: 6500 -> 5750K)
hl.unbind("SUPER + CTRL + N")
o.bind("SUPER + CTRL + N", "Toggle night light (suave)", "gran-nightlight-soft")

-- Rename file in the file manager (Nautilus): SHIFT + ENTER sends F2.
o.bind("SHIFT + RETURN", "Rename selected file (F2)", "@@GRAN_HOME@@/.local/bin/rename-selected")

-- OpenCode: SUPER + SHIFT + O (was: Obsidian from the preinstalled bindings)
hl.unbind("SUPER + SHIFT + O")
o.bind("SUPER + SHIFT + O", "OpenCode", { tui = "opencode", focus = true })

-- GranCtrl: SUPER + SHIFT + G (was: Signal from the preinstalled bindings)
hl.unbind("SUPER + SHIFT + G")
o.bind("SUPER + SHIFT + G", "GranCtrl", { launch = "GranCtrl.desktop" })

-- Keep Warp on SUPER + SHIFT + T and move the default Activity binding.
o.rebind("SUPER + SHIFT + T", "Terminal (Warp)", { launch = "warp-terminal" })
o.bind("CTRL + SUPER + ALT + T", "Activity", { tui = "btop" })

-- Keyboard backlight: save the chosen level as the persistent default
-- (restored on boot and on resume). Wrapper shadows gran-brightness-keyboard.
hl.unbind("XF86KbdBrightnessUp")
hl.unbind("XF86KbdBrightnessDown")
hl.unbind("XF86KbdLightOnOff")
o.bind("XF86KbdBrightnessUp", "Keyboard brightness up (persist)", "@@GRAN_HOME@@/.local/bin/gran-brightness-keyboard up", { locked = true, repeating = true })
o.bind("XF86KbdBrightnessDown", "Keyboard brightness down (persist)", "@@GRAN_HOME@@/.local/bin/gran-brightness-keyboard down", { locked = true, repeating = true })
o.bind("XF86KbdLightOnOff", "Keyboard backlight cycle (persist)", "@@GRAN_HOME@@/.local/bin/gran-brightness-keyboard cycle", { locked = true })

-- Resize current window with CTRL + arrows (grows current, shrinks others)
o.bind("SUPER + CTRL + LEFT", "Expand window left", hl.dsp.window.resize({ x = -100, y = 0, relative = true }))
o.bind("SUPER + CTRL + RIGHT", "Expand window right", hl.dsp.window.resize({ x = 100, y = 0, relative = true }))
o.bind("SUPER + CTRL + UP", "Expand window up", hl.dsp.window.resize({ x = 0, y = -100, relative = true }))
o.bind("SUPER + CTRL + DOWN", "Expand window down", hl.dsp.window.resize({ x = 0, y = 100, relative = true }))

-- Exposé (window overview) on ALT + TAB (was: focus next window)
o.rebind("ALT + TAB", "Exposé", hl.dsp.event("expose.window-overview:toggle"))

-- Virtual Machine Manager: SUPER + SHIFT + V. Runs as the user -- the
-- libvirt group membership grants access to qemu:///system, so no sudo is
-- needed (pkexec was dropped: it strips the Wayland display env and the
-- GUI never opens).
o.bind("SUPER + SHIFT + V", "Virtual Machine Manager", { launch = "virt-manager" })

-- Terminal TUIOS: CTRL + SUPER + U
o.bind("CTRL + SUPER + U", "TUIOS Terminal", { tui = "tuios", focus = true })

-- Logitech MX Keys examples:
-- o.bind("SUPER + SHIFT + S", nil, "gran-capture-screenshot")
-- o.bind("SUPER + H", nil, "voxtype record toggle")
-- o.bind("SUPER + PERIOD", nil, "gran-shell shell toggle gran.emojis")

-- Bloquear sempre ao fechar a tampa, inclusive com monitor externo.
o.rebind("switch:on:Lid Switch", "Bloquear ao fechar a tampa", "gran system lock; gran-hyprland-monitor-clamshell", { locked = true })

-- Ao abrir a tampa, ligar a tela e exibir o bloqueio durante a retomada.
o.rebind("switch:off:Lid Switch", "Ligar tela ao abrir a tampa", "@@GRAN_HOME@@/.local/bin/gran-lid-open-wake", { locked = true })

-- fathom: begin
do
  local fathom = os.getenv("HOME") .. "/.config/gran/plugins/io.github.mtolhuys.fathom/hypr/fathom.lua"
  local file = io.open(fathom, "r")
  if file then
    file:close()
    pcall(dofile, fathom)
  end
end
-- fathom: end

-- Chromium (localhost:3000): CTRL + SUPER + Ç.
-- A tecla Ç do ABNT2 tem o keysym "ccedilla".
o.bind("SUPER + CTRL + ccedilla", "Chromium (localhost:3000)", { launch = "chromium http://localhost:3000" })

-- Nautilus: file manager shortcuts.
o.rebind("SUPER + SHIFT + F", "File manager", { launch = "@@GRAN_HOME@@/.local/bin/nautilus-remember --new-window" })
o.rebind("SUPER + ALT + SHIFT + F", "File manager (cwd)", { launch = '@@GRAN_HOME@@/.local/bin/nautilus-remember --new-window "$(gran-cmd-terminal-cwd)"' })


-- Keep the agent's top-down console on SUPER + S, even when Gran changes
-- its default bindings. Replaces the empty scratchpad toggle from the defaults.
o.rebind("SUPER + S", "Agent (top-down console)", hl.dsp.workspace.toggle_special("qconsole"))
