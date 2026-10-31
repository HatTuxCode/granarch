# Sources and updates

Hyprland, Quickshell, Kitty, fish and mise come from official Arch core/extra
packages. Those packages build the respective upstream projects. The installer
does not add repositories or change mirrors. Never enable a third-party desktop
distribution repository to fix a missing Gran helper.

Zen is downloaded from `zen-browser/desktop` GitHub releases. The `gran app`
helper verifies its SHA-256 digest before extraction. Yaru is built from an
identified commit of `ubuntu/yaru`; it provides the inherited icons/cursor.
`gran app sources` lists direct sources, and `gran app update installed`
updates only applications already managed by that helper.

Node LTS, Codex CLI and OpenCode are managed by mise. Use
`mise ls` to inspect them. `gran update` combines pacman, mise and upstream
application updates. It does not rewrite the desktop source tree or overwrite
personal configurations. Use the GranArch project to distribute desktop changes.

Apps referenced by inherited shortcuts are optional. Install only what the user
requests. Source integrations such as Proton VPN, camera effects, dictation or
upstream hyprbars require their own packages/builds; their preserved shortcuts
do not authorize installing a full application suite.
