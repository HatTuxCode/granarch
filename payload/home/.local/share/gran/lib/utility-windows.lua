-- Build real dispatchers separately so validation can exercise their API.
local function utility_actions(window)
 return {
  hl.dsp.window.fullscreen({mode = "fullscreen", action = "unset", window = window}),
  hl.dsp.window.fullscreen({mode = "maximized", action = "unset", window = window}),
  hl.dsp.window.float({action = "on", window = window}),
  hl.dsp.window.resize({x = 875, y = 600, relative = false, window = window}),
  hl.dsp.window.center({window = window}),
 }
end
local function center_utility(window)
 if not window then return end
 local class = window.class or ""
 if class ~= "org.gran.btop" and class ~= "org.gran.update" and class ~= "org.gran.gran-launch-docker-tui" then return end
 hl.timer(function()
  for _, dispatcher in ipairs(utility_actions(window)) do hl.dispatch(dispatcher) end
 end, {type = "oneshot", timeout = 1})
end
hl.on("window.open", center_utility)
for _, window in ipairs(hl.get_windows()) do center_utility(window) end
return { actions = utility_actions }

