-- Two workspace layouts; restore only windows tagged by the retired floating mode.
local tag = "gran-mode-floated"
local function arrange()
 for _, w in ipairs(hl.get_windows({ tag = tag })) do
  if not w.pinned then
   hl.dispatch(hl.dsp.window.tag({ tag = "-" .. tag, window = w }))
   hl.dispatch(hl.dsp.window.float({ action = "off", window = w }))
  end
 end
end
function gran_workspace_mode(spec)
 local mode = spec.default or spec.mode
 if mode ~= "dwindle" and mode ~= "scrolling" then error("Use dwindle ou scrolling") end
 if spec.default then
  hl.config({ general = { layout = mode } })
 else
  hl.workspace_rule({ workspace = tostring(spec.workspace), layout = mode })
 end
 arrange()
end
local path = (os.getenv("XDG_STATE_HOME") or (os.getenv("HOME") .. "/.local/state")) .. "/gran/workspace-layouts/modes"
local file = io.open(path, "r")
if file then
 for line in file:lines() do
  local id, mode = line:match("^(%w+) (%a+)$")
  if mode == "floating" then mode = "dwindle" end
  if mode == "dwindle" or mode == "scrolling" then
   if id == "default" then gran_workspace_mode({ default = mode })
   elseif tonumber(id) then gran_workspace_mode({ workspace = id, mode = mode }) end
  end
 end
 file:close()
end
arrange()
