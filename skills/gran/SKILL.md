---
name: gran
description: Customize or troubleshoot the GranArch desktop, including its Hyprland bindings, Quickshell bar, themes, Kitty, fish and gran commands. Use for changes to Gran desktop behavior or appearance; not for unrelated application development.
---

# Gran desktop

GranArch uses upstream Hyprland and Quickshell from official Arch packages.
The desktop sources and utilities live at `$GRAN_PATH`, normally
`~/.local/share/gran`. User overrides live in `~/.config/hypr`,
`~/.config/gran`, `~/.config/kitty` and `~/.config/fish`.
Theme state is `~/.local/state/gran/current`. There is no distribution package
repository, keyring or migration service to enable.

Use `gran commands` to discover real commands before proposing a command.
`gran update` updates Arch packages, selected mise tools and directly managed
upstream applications. `gran doctor` checks the desktop; `gran skills list`
shows these instructions. Read [desktop.md](references/desktop.md) for config
locations and validation and [packages.md](references/packages.md) for sources.

Preserve existing shortcut combinations, including shortcuts for optional apps.
Before rebinding, inspect `hyprctl -j binds` and `~/.config/hypr/bindings.lua`.
Change a conflicting binding with `o.rebind`; describe any action it replaces.
Use the installed Hyprland version and current upstream documentation for Lua
rules. After editing Lua, run `hyprctl reload` and `hyprctl configerrors` when a
session is available. A syntax check alone does not prove runtime compatibility.

Apply user customization through override files; change runtime sources in the
GranArch project when a change must survive reinstalling. Back up existing
files. Do not import browser sessions, credentials, clipboard or shell history
into desktop exports. Keep agent permissions and account authentication under
the user's control; desktop integration does not require bypass flags.
