-- GranHat: standalone Hyprland >=0.55 + Noctalia. No Omarchy runtime.
hl.monitor({ output = "", mode = "preferred", position = "auto", scale = 1.25 })
hl.config({
 general = { layout = "dwindle", gaps_in = 3, gaps_out = 6, border_size = 2,
   resize_on_border = true, col = { active_border = "rgb(81a1c1)", inactive_border = "rgb(434c5e)" } },
 dwindle = { preserve_split = true, force_split = 2 },
 input = { kb_layout = "br", kb_model = "abnt2", kb_options = "shift:both_capslock_cancel",
   repeat_delay = 250, repeat_rate = 40, follow_mouse = 1,
   touchpad = { natural_scroll = true, tap_to_click = true, drag_3fg = 1 } },
 decoration = { rounding = 4, active_opacity = 0.90, inactive_opacity = 0.60,
   fullscreen_opacity = 0.90, shadow = { enabled = false },
   blur = { enabled = true, popups = true, popups_ignorealpha = 0.2, size = 14, passes = 2, noise = 0.0117, contrast = 0.8916,
     brightness = 1.0, vibrancy = 0.1696, xray = false } },
 cursor = { hide_on_key_press = true },
 misc = { disable_hyprland_logo = true, disable_splash_rendering = true },
})
hl.window_rule({ match = { class = ".*" }, suppress_event = "maximize" })
hl.window_rule({ match = { class = ".*" }, opacity = "0.90 override 0.60 override 0.90 override" })
hl.window_rule({ match = { class = "^(org\\.gran\\.update|org\\.gran\\.btop|org\\.gran\\.gran-launch-docker-tui)$" },
 float = true, center = true, size = {875, 600}, fullscreen_state = "0 0", suppress_event = "maximize fullscreen" })
local theme = os.getenv("HOME") .. "/.config/hypr/noctalia.lua"
local file = io.open(theme, "r")
if file then file:close(); dofile(theme).apply_theme() end
local function spawn(keys, command, options) hl.bind(keys, hl.dsp.exec_cmd(command), options or {}) end
spawn("SUPER + RETURN", "gran-launch-terminal")
spawn("CTRL + SUPER + RETURN", "gran-launch-terminal --directory @HOME@/Work @HOME@/.local/bin/tuios")
spawn("SUPER + SHIFT + T", "gran-launch-terminal")
spawn("SUPER + D", "gran-launch-dolphin")
spawn("SUPER + SHIFT + F", "gran-launch-dolphin")
spawn("SUPER + ALT + SHIFT + F", "gran-launch-dolphin-cwd")
spawn("SUPER + SHIFT + RETURN", "zen-browser")
spawn("SUPER + SHIFT + B", "zen-browser")
spawn("SUPER + ALT + RETURN", "gran-launch-codex")
spawn("SUPER + ALT + O", "gran-launch-opencode")
spawn("CTRL + SUPER + ALT + T", "gran-launch-tui btop")
spawn("SUPER + SPACE", "noctalia msg panel-toggle launcher")
spawn("SUPER + S", "noctalia msg panel-toggle control-center")
spawn("SUPER + SHIFT + COMMA", "noctalia msg settings-toggle")
spawn("SUPER + ESCAPE", "noctalia msg panel-toggle session")
spawn("SUPER + CTRL + L", "noctalia msg session lock")
hl.bind("SUPER + Q", hl.dsp.window.close())
hl.bind("SUPER + F", hl.dsp.window.fullscreen({ mode = "fullscreen" }))
hl.bind("SUPER + ALT + M", hl.dsp.window.fullscreen({ mode = "maximized" }))
hl.bind("SUPER + T", hl.dsp.window.float({ action = "toggle" }))
hl.bind("SUPER + J", hl.dsp.layout("togglesplit"))
hl.bind("SUPER + P", hl.dsp.window.pseudo())
hl.bind("SUPER + ALT + H", hl.dsp.window.move({ workspace = "special:stash", follow = false }))
hl.bind("SUPER + CTRL + H", hl.dsp.workspace.toggle_special("stash"))
hl.bind("ALT + TAB", hl.dsp.window.cycle_next())
for key, dir in pairs({ LEFT = "l", RIGHT = "r", UP = "u", DOWN = "d" }) do
 hl.bind("SUPER + " .. key, hl.dsp.focus({ direction = dir }))
 hl.bind("SUPER + SHIFT + " .. key, hl.dsp.window.swap({ direction = dir }))
end
for key, delta in pairs({ LEFT = {-100,0}, RIGHT = {100,0}, UP = {0,-100}, DOWN = {0,100} }) do
 hl.bind("SUPER + CTRL + " .. key, hl.dsp.window.resize({ x = delta[1], y = delta[2], relative = true }))
end
for i = 1, 10 do
 local key = "code:" .. tostring(i + 9)
 hl.bind("SUPER + " .. key, hl.dsp.focus({ workspace = tostring(i) }))
 hl.bind("SUPER + SHIFT + " .. key, hl.dsp.window.move({ workspace = tostring(i), follow = true }))
end
hl.bind("SUPER + mouse:272", hl.dsp.window.drag(), { mouse = true })
hl.bind("SUPER + mouse:273", hl.dsp.window.resize(), { mouse = true })
for key, command in pairs({
 XF86AudioRaiseVolume = "wpctl set-volume -l 1 @DEFAULT_AUDIO_SINK@ 5%+",
 XF86AudioLowerVolume = "wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-",
 XF86AudioMute = "wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle",
 XF86AudioMicMute = "wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle",
 XF86MonBrightnessUp = "brightnessctl -c backlight set +5%",
 XF86MonBrightnessDown = "brightnessctl -c backlight set 5%-",
 XF86KbdBrightnessUp = "gran-brightness-keyboard up",
 XF86KbdBrightnessDown = "gran-brightness-keyboard down",
 XF86KbdLightOnOff = "gran-brightness-keyboard cycle",
 XF86AudioPlay = "playerctl play-pause", XF86AudioPause = "playerctl play-pause",
 XF86AudioNext = "playerctl next", XF86AudioPrev = "playerctl previous",
}) do spawn(key, command, { locked = true, repeating = true }) end
hl.on("hyprland.start", function()
 hl.exec_cmd("gran-session-ready")
 hl.exec_cmd("udiskie --automount --no-notify --no-tray")
end)

dofile(os.getenv("HOME") .. "/.local/share/gran/lib/workspace-layouts.lua")
spawn("SUPER + L", "gran-hyprland-workspace-layout-toggle")
spawn("SUPER + ALT + L", "gran-hyprland-workspace-layout-toggle back")

hl.window_rule({ match = { class = "^(org\\.kde\\.dolphin|dolphin)$", float = true },
 opacity = "1.0 override 1.0 override 1.0 override" })

spawn("SUPER + CTRL + ccedilla", "gran-launch-chromium http://localhost:3000")

spawn("XF86TouchpadToggle", "gran-touchpad toggle", { locked = true })
spawn("XF86TouchpadOn", "gran-touchpad on", { locked = true })
spawn("XF86TouchpadOff", "gran-touchpad off", { locked = true })
spawn("SHIFT + XF86MonBrightnessUp", "brightnessctl -c backlight set 100%", { locked = true })
spawn("SHIFT + XF86MonBrightnessDown", "brightnessctl -c backlight set 1%", { locked = true })

spawn("SUPER + O", "gran-hyprland-window-pop 1000 650")
spawn("XF86PowerOff", "noctalia msg panel-toggle session", { locked = true })

dofile(os.getenv("HOME") .. "/.local/share/gran/lib/utility-windows.lua")

-- Kitty must enter tiled mode rather than restore a previous maximize request.
hl.window_rule({ match = { class = "^(kitty|org\\.gran\\.terminal)$" },
 fullscreen_state = "0 0", suppress_event = "maximize" })

dofile(os.getenv("HOME") .. "/.local/share/gran/lib/workspace-indicator.lua")

-- For Noctalia Color templates
require("noctalia").apply_theme()

spawn("Print", "gran-screenshot")
spawn("SHIFT + Print", "gran-screenshot region")

spawn("SUPER + SHIFT + D", "gran-launch-tui gran-launch-docker-tui")
dofile(os.getenv("HOME") .. "/.local/share/gran/lib/clipboard.lua")

-- Image viewer: use the image geometry supplied by its launcher.
hl.window_rule({ match = { class = "^(imv)$" }, float = true, center = true })

-- Keep virt-manager dialogs within the usable monitor area.
hl.window_rule({ match = { class = "^(virt-manager)$", float = true },
 center = true, size = {900, 600}, fullscreen_state = "0 0", suppress_event = "maximize" })
