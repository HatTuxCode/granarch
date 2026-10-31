---
name: gran-diagnose
description: Diagnose GranArch desktop failures, including Hyprland or Quickshell startup, a missing bar, failed lock screen, or a desktop process crash. Use for an observed desktop failure, not routine appearance changes.
---

# Diagnose a Gran desktop failure

Start with `gran doctor`, the installed package versions and
`journalctl --user -b -t gran-shell`. Use `hyprctl configerrors` inside the
affected session. Separate a Lua/QML configuration error from a process crash;
do not reset the user's configuration as an initial diagnostic step.

For an actual core dump, inspect `coredumpctl list`, select the exact process,
then inspect its metadata and a symbolized backtrace if tools/symbols are
available. State which evidence confirms the cause and which parts remain
uncertain. Core dumps and logs can contain private data; do not publish them or
send an upstream report without the user's request.

The engines come from upstream projects through official Arch packages, while
the local desktop sources live in `$GRAN_PATH`. Check their API compatibility
before attributing a failure. Reproduce a proposed fix in an isolated profile
or VM where practical. Preserve user overrides and restore changed test files.
Do not restart the Quickshell process while it owns an active session lock;
inspect the lock status and use another TTY for recovery if needed.
