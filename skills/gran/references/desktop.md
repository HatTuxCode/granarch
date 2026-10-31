# Configuration and validation

Hyprland starts from `~/.config/hypr/hyprland.lua` and loads Gran's defaults
from `$GRAN_PATH/default/hypr/` before user modules. `bindings.lua` contains
personal key choices, `monitors.lua` contains scale/output rules, `input.lua`
contains keyboard/touchpad rules, and `looknfeel.lua` contains gaps, blur,
rounding and opacity. The source profile includes ASUS-specific device names.

The bar, notifications, launcher and lock screen run in one Quickshell shell.
Its layout is `~/.config/gran/shell.json`; appearance overrides are in
`shell.toml`. Custom plugins are under `~/.config/gran/plugins/`, including
`hattux.bar`. Stock plugin IDs start with `gran.`. Changing an ID requires
updating manifests, layout references, QML IPC targets and callbacks together.

The theme is Nord. Resolved files are in `~/.local/state/gran/current/theme`;
the wallpaper link is `~/.local/state/gran/current/background`.
Use `gran theme --help`, `gran bar --help` and `gran restart shell --help`
for the installed interfaces. Shell restarts must respect an active lock.

Kitty includes the resolved theme palette. fish activates mise and Starship;
the login environment comes from UWSM and the installed profile.d fragment.
Zen is the default browser. `Super+Enter` launches the default terminal and
`Super+S` toggles the agent console. Existing optional application bindings
are intentionally retained even when the corresponding app is absent.

Check config changes in the running session with `gran doctor`,
`hyprctl configerrors` and `journalctl --user -b -t gran-shell`.
In a headless environment, check syntax and report that session behavior remains
unverified; do not reload another user's compositor.

The notebook policy is `~/.config/gran/notebook.json`. The captured profile uses
30s keyboard-light idle on battery, 20min screen idle only at <=25% battery,
performance on AC, balanced on battery, power-saver at <=25% and a 95% charge
limit. ASUS firmware/EPP settings are supplied by upstream asusctl on ASUS;
Intel machines also use upstream thermald. Preserve lid lock and the sleep
inhibitor when changing power behavior. UPower percentage is a fraction 0..1
in the upstream Quickshell API; convert before comparing to a 0..100 threshold.

Boot appearance uses Plymouth; SDDM autologin starts Gran after disk unlock.
The bootloader and disk encryption belong to the destination installation.
Never transplant UUIDs, PARTUUIDs, swap offsets or unlock keys from an export.
Use `gran theme sync` to regenerate shared GTK/Qt/Zen palette integration.
Apps with embedded or sandboxed themes may need their own adapter.

The launcher is Gran's inherited Quickshell AppGrid: `gran launch apps`.
The full menu includes Install, Remove and Setup. Use `gran pkg install` and
`gran pkg remove` for interactive pacman transactions; `gran webapp install`
creates a launcher for a site. Chromium app windows are optional and do not
replace Zen as the default browser. `gran setup` exposes defaults, keyboard,
Git, network and other desktop settings. Optional app catalog entries are
installed only when selected, never as a preinstalled suite.
