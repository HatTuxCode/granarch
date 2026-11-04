-- Keep 1..last occupied/current workspace plus one empty workspace in Noctalia.
-- Do not use the number of persistent workspaces as input: that grows forever.
local previous_end = 0
local pending = false
local managed = {}
local closing = {}
local function positive_id(value)
 local id = tonumber(value)
 return id and id >= 1 and id == math.floor(id) and id or nil
end
local function desired_end(windows, active)
 local highest = positive_id(active and active.id) or 1
 for _, window in ipairs(windows) do
  local id = positive_id(window.workspace and window.workspace.id)
  if id and not closing[window.address] then highest = math.max(highest, id) end
 end
 return highest + 1
end
local function persist(id, enabled)
 if managed[id] == enabled then return end
 hl.workspace_rule({ workspace = tostring(id), persistent = enabled })
 managed[id] = enabled
end
local function refresh()
 pending = false
 local windows = hl.get_windows()
 local occupied = {}
 for _, window in ipairs(windows) do
  local id = positive_id(window.workspace and window.workspace.id)
  if id and not closing[window.address] then occupied[id] = true end
 end
 local active = hl.get_active_workspace()
 local last = desired_end(windows, active)
 for id = 1, last do
  persist(id, true)
 end
 local existing_end = previous_end
 for _, workspace in ipairs(hl.get_workspaces()) do
  local id = positive_id(workspace.id)
  if id then
   existing_end = math.max(existing_end, id)
   local label = occupied[id] and "●" or "​" -- Invisible label preserves the native empty circle.
   if workspace.name ~= label then
    hl.dispatch(hl.dsp.workspace.rename({ workspace = tostring(id), name = label }))
   end
  end
 end
 for id = last + 1, existing_end do
  persist(id, false)
 end
 previous_end = last
 closing = {}
end
local function schedule()
 if pending then return end
 pending = true
 hl.timer(refresh, { type = "oneshot", timeout = 10 })
end
hl.on("window.open", schedule)
hl.on("window.close", function(window)
 if window and window.address then closing[window.address] = true end
 schedule()
end)
hl.on("window.move_to_workspace", schedule)
hl.on("workspace.active", schedule)
hl.on("workspace.created", schedule)
hl.on("monitor.focused", schedule)
refresh()
return { refresh = refresh, desired_end = desired_end }
