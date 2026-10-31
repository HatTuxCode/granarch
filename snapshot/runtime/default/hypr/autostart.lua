require("default.hypr.startup-cursor")

hl.on("hyprland.start", function()
  -- Applications inherit the user's cursor; only the compositor starts blank.
  if gran_startup_cursor_pending then
    hl.env("XCURSOR_PATH", gran_startup_cursor.path)
    hl.env("XCURSOR_THEME", gran_startup_cursor.xcursor)
  end

  -- Slow app launch fix -- set systemd and D-Bus activation vars before
  -- starting session services.
  hl.exec_cmd("dbus-update-activation-environment --systemd --all")

  hl.exec_cmd("gran-launch-shell")
  hl.exec_cmd("gran-provision-first-run")
  hl.exec_cmd("gran-powerprofiles-init")
  hl.exec_cmd(o.launch("gran-hyprland-monitor-watch"))
  hl.exec_cmd(o.launch("udiskie --automount --no-notify --no-tray"))

  -- Start the herdr server inside the graphical session so its panes inherit
  -- WAYLAND_DISPLAY. Otherwise the first SSH login from a remote herdr starts
  -- it with a tty environment, and agents in its panes can't read the clipboard.
  hl.exec_cmd(o.launch("herdr server"))

  -- Run post-boot hooks after startup config has loaded.
  hl.exec_cmd("sleep 2 && gran-hook post-boot")
end)
