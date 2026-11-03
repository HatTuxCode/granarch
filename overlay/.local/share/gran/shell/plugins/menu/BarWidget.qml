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
    text: ""
    iconComponent: Component {
      Item {
        width: 48
        height: 52

        // The same double-line G as the fastfetch art, in terminal-cell proportions.
        Repeater {
          model: [
            [0, 0, 48, 4], [0, 0, 4, 52], [0, 48, 48, 4],
            [44, 24, 4, 28], [8, 8, 32, 4], [8, 8, 4, 36],
            [8, 40, 32, 4], [36, 24, 4, 20], [24, 24, 24, 4]
          ]
          Rectangle {
            required property var modelData
            x: modelData[0]
            y: modelData[1]
            width: modelData[2]
            height: modelData[3]
            color: button.foreground
            antialiasing: true
          }
        }
      }
    }
    fontFamily: root.bar ? root.bar.fontFamily : "monospace"
    onPressed: function(button) {
      if (!root.bar) return
      if (button === Qt.RightButton) root.bar.run("xdg-terminal-exec")
      else root.bar.run("gran-shell shell toggle gran.menu '{\"menu\":\"root\"}'")
    }
  }
}
