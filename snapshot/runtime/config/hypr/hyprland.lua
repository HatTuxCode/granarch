-- Learn how to configure Hyprland: https://wiki.hypr.land/Configuring/Start/

-- Gran's bootstrap keeps path setup out of this user config.
dofile((os.getenv("GRAN_PATH") or "/usr/share/gran") .. "/default/hypr/bootstrap.lua")

-- Disable all Gran default bindings. Add your own in hypr/bindings.lua.
-- gran_default_bindings = false
--
-- Or disable only bindings for Gran's preinstalled apps/web apps while
-- keeping core window-manager bindings:
-- gran_preinstalled_bindings = false
--
-- Disable Gran's default touchpad gestures. Add your own in hypr/input.lua.
-- gran_default_gestures = false

-- Load Gran defaults.
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
