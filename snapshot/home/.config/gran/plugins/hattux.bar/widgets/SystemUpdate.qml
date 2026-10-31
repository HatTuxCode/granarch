import QtQuick
import Quickshell
import Quickshell.Io
import qs.Commons
import qs.Ui

BarWidget {
  id: root
  moduleName: "gran.system-update"

  property bool updateAvailable: false

  function refresh() {
    if (!updateProc.running) updateProc.running = true
  }

  function clear() { updateAvailable = false }

  function runUpdate() {
    if (root.bar) root.bar.run("gran-launch-floating-terminal-with-presentation \"$HOME/.local/bin/gran-update-preserve-bar\"")
  }

  visible: updateAvailable
  implicitWidth: button.implicitWidth
  implicitHeight: button.implicitHeight

  ShellIpc {
    target: "gran.system-update"

    function refresh(): void {
      root.broadcast("refresh")
    }

    function clear(): void {
      root.broadcast("clear")
    }
  }

  Process {
    id: updateProc
    command: ["gran-update-available"]
    onExited: function(exitCode) {
      root.updateAvailable = exitCode === 0
    }
  }

  Timer {
    interval: 21600000
    running: true
    repeat: true
    triggeredOnStart: true
    onTriggered: root.refresh()
  }

  BarIconButton {
    id: button
    anchors.fill: parent
    bar: root.bar
    text: "\uf021"
    slotSize: Style.bar.statusSlot
    tooltipText: "Pending Gran Updates"
    onPressed: root.runUpdate()
  }
}
