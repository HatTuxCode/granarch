-- Learn how to configure Hyprland: https://wiki.hypr.land/Configuring/Start/

-- Gran's bootstrap keeps path setup out of this user config.
dofile((os.getenv("GRAN_PATH") or "/usr/share/gran") .. "/default/hypr/bootstrap.lua")

-- Disable all Gran default bindings. Add your own in hypr/bindings.lua.
-- gran_default_bindings = false
--
-- Or disable only bindings for Gran's preinstalled apps/web apps while
-- keeping core window-manager bindings:
-- gran_preinstalled_bindings = false

-- Load Gran defaults.
-- Your own gestures replace Gran's defaults.
gran_default_gestures = false

require("default.hypr.gran")

-- Put your personal overrides in these files. They're loaded after Gran's
-- defaults so package updates can improve the defaults without rewriting your
-- ~/.config/hypr files.
require("hypr.monitors")
require("hypr.input")
require("hypr.bindings")
require("hypr.looknfeel")
require("hypr.autostart")

-- Toggle config flags dynamically.
require("default.hypr.toggles")

-- Add any other personal Hyprland configuration below.
-- o.window("qemu", { workspace = "5" })

-- GranControl: janela flutuante do atalho da barra com cantos bem arredondados.
o.window("chrome-www%.grancontrol%.app.*", { rounding = 20 })

-- Load settings written by OmaSettings (omasettings:managed).
require("hypr.omasettings")

-- Opacidade uniforme, incluindo o agente no Super+S.
o.window(".*", { opacity = "0.90 override 0.60 override 0.90 override" })

-- Cantos quadrados apenas na janela do agente (Super+S).
o.window("org\\.gran\\.agent", { rounding = 0 })
