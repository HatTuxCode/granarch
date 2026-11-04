--!nonstrict
local checking = false
barWidget.setGlyph("refresh")
barWidget.setText("")
barWidget.setTooltip("Atualizações GranHat — clique para atualizar")
noctalia.setUpdateInterval(60000)
function update()
 if checking then return end
 checking = true
 local accepted = noctalia.runAsync("gran-update-check", function(result)
  checking = false
  local count = tonumber(result.stdout)
  if result.exitCode ~= 0 or count == nil then
   barWidget.setText("?")
   barWidget.setTooltip("Não foi possível verificar atualizações. Clique para abrir o atualizador.")
  else
   barWidget.setText(count > 0 and tostring(count) or "")
   barWidget.setGlyphColor(count > 0 and "primary" or "on_surface")
   barWidget.setTooltip(count > 0 and (tostring(count) .. " atualizações Arch disponíveis — clique para atualizar") or "Sistema atualizado — clique para verificar/atualizar também mise e apps")
  end
 end)
 if not accepted then checking = false end
end
function onClick() noctalia.runAsync("gran-launch-update") end
function onRightClick() noctalia.runAsync("gran-update-check --refresh", function(_) update() end) end
update()
