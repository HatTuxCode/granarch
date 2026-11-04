import QtQuick 2.15
Rectangle {
    color: "#2e3440"
    function onActivate() {}
    function onLeave() {}
    Text {
        anchors.centerIn: parent
        width: parent.width * 0.85
        horizontalAlignment: Text.AlignHCenter
        wrapMode: Text.WordWrap
        color: "#d8dee9"
        text: qsTr("GranArch\nArch Linux + Hyprland + Noctalia")
    }
}
