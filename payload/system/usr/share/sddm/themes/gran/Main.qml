import QtQuick 2.15
import QtQuick.Effects
Rectangle {
    id: root
    width: 1280; height: 720
    color: "#2e3440"
    property int sessionIndex: -1
    property string message: ""
    property string loginUser: userModel.lastUser
    Image {
        id: wallpaper
        anchors.fill: parent
        source: "background.jpg"
        fillMode: Image.PreserveAspectCrop
        visible: false
    }
    MultiEffect {
        anchors.fill: parent
        source: wallpaper
        blurEnabled: true
        blurMax: 64
        blur: 1.0
    }
    Rectangle { anchors.fill: parent; color: "#55000000" }
    function login() {
        if (root.loginUser.length && sessionIndex >= 0)
            sddm.login(root.loginUser, password.text, sessionIndex)
        else message = "Sessão GranArch ou usuário indisponível."
    }
    Repeater {
        model: userModel
        delegate: Item {
            visible: false
            Component.onCompleted: {
                if (root.loginUser.length === 0 && model.name)
                    root.loginUser = model.name
            }
        }
    }
    // Instantiate only hidden session records to find granarch.desktop reliably.
    Repeater {
        model: sessionModel
        delegate: Item {
            visible: false
            Component.onCompleted: {
                if (model.file === "granarch.desktop" || model.file.endsWith("/granarch.desktop") || model.file === "granarch-live.desktop" || model.file.endsWith("/granarch-live.desktop"))
                    root.sessionIndex = index
            }
        }
    }
    Connections {
        target: sddm
        function onLoginFailed() {
            root.message = "Senha incorreta. Tente novamente."
            password.text = ""
            password.forceActiveFocus()
        }
    }
    Column {
        anchors.centerIn: parent
        width: 300; spacing: 12
        Rectangle {
            width: parent.width; height: 44; radius: 6; color: "#dd2e3440"
            border.color: "#6688c0d0"
            Text {
                anchors.centerIn: parent
                visible: password.text.length === 0
                text: "Senha"; color: "#adb5c4"; font.pixelSize: 16
            }
            TextInput {
                id: password
                anchors.fill: parent; anchors.margins: 12
                color: "#eceff4"; font.pixelSize: 16
                horizontalAlignment: TextInput.AlignHCenter
                echoMode: TextInput.Password
                focus: true; activeFocusOnTab: true
                Keys.onReturnPressed: root.login()
                Keys.onEnterPressed: root.login()
            }
        }
        Text { text: root.message; color: "#ef9a9a"; width: parent.width; wrapMode: Text.WordWrap; horizontalAlignment: Text.AlignHCenter }
    }
    Component.onCompleted: password.forceActiveFocus()
}
