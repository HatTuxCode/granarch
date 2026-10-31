import QtQuick
import qs.Ui

BarWidget {
  id: root
  moduleName: "gran.menu"

  implicitWidth: button.implicitWidth
  implicitHeight: button.implicitHeight

  BarIconButton {
    id: button
    anchors.fill: parent
    bar: root.bar
    text: "G"
    fontFamily: root.bar ? root.bar.fontFamily : "monospace"
    onPressed: function(button) {
      if (!root.bar) return
      if (button === Qt.RightButton) root.bar.run("xdg-terminal-exec")
      else root.bar.run("gran-shell shell toggle gran.menu '{\"menu\":\"root\"}'")
    }
  }
}
