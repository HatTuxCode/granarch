import QtQuick
import Quickshell
import Quickshell.Io
import Quickshell.Wayland

Item {
  id: root

  property var shell: null

  readonly property string home: Quickshell.env("HOME")
  readonly property int idleTimeoutSeconds: 30

  property string lastCommand: ""

  function run(command) {
    root.lastCommand = command
    if (backlightProcess.running) return
    backlightProcess.command = ["bash", "-lc", command]
    backlightProcess.running = true
  }

  IdleMonitor {
    id: idleMonitor
    timeout: root.idleTimeoutSeconds
    respectInhibitors: false
    onIsIdleChanged: {
      if (idleMonitor.isIdle) root.run("~/.local/bin/gran-kbd-backlight-idle idle")
      else root.run("~/.local/bin/gran-kbd-backlight-idle active")
    }
  }

  Process {
    id: backlightProcess
    onRunningChanged: {
      if (!running && root.lastCommand && typeof (backlightProcess.command[2]) === "string"
          && backlightProcess.command[2] !== root.lastCommand) {
        var pending = root.lastCommand
        root.lastCommand = ""
        root.run(pending)
      }
    }
  }

  Component.onCompleted: {
    // A shell restart recreates IdleMonitor while the session is already
    // active, so isIdleChanged does not fire to restore a saved brightness.
    // Restore it once at startup; IdleMonitor will turn it off again if the
    // user is genuinely idle.
    root.run("~/.local/bin/gran-kbd-backlight-idle active")
    console.log("gran kbd-backlight-idle service loaded, idle timeout " + root.idleTimeoutSeconds + "s")
  }
}
