-- Adapt Omarchy's explicit down/up dispatch to GranHat's terminal classes.
local function copy_or_paste(key)
 return function()
  local w = hl.get_active_window()
  local cls = w and w.class or ""
  local terminal = cls == "kitty" or cls:match("^org%.gran%.") or cls == "Alacritty" or cls == "foot" or cls == "com.mitchellh.ghostty"
  local mods = terminal and "CTRL SHIFT" or "CTRL"
  hl.dispatch(hl.dsp.send_key_state({mods = mods, key = key, state = "down"}))
  hl.timer(function()
   hl.dispatch(hl.dsp.send_key_state({mods = mods, key = key, state = "up"}))
  end, {timeout = 50, type = "oneshot"})
 end
end
hl.bind("SUPER + C", copy_or_paste("C"))
hl.bind("SUPER + V", copy_or_paste("V"))
hl.bind("CTRL + SHIFT + C", hl.dsp.exec_cmd("noctalia msg panel-toggle clipboard"))
hl.bind("SUPER + CTRL + V", hl.dsp.exec_cmd("noctalia msg panel-toggle clipboard"))
