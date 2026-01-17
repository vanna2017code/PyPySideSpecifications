import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    width: 600
    height: 450
    visible: true
    title: "SpecShower Installer"

    Column {
        anchors.centerIn: parent
        spacing: 10

        TextField {
            id: repoField
            placeholderText: "GitHub repo URL"
            text: "https://github.com/yourusername/specshower.git"
            width: parent.width * 0.8
        }

        TextField {
            id: dirField
            placeholderText: "Install directory"
            text: "specshower_app"
            width: parent.width * 0.8
        }

        Button {
            text: "Install"
            onClicked: installer.runInstall(repoField.text, dirField.text)
        }

        Button {
            text: "Launch App"
            onClicked: installer.launchApp(dirField.text)
        }

        TextArea {
            id: logArea
            width: parent.width * 0.9
            height: 200
            readOnly: true
        }
    }

    Connections {
        target: installer
        onLogOutput: logArea.text += text + "\n"
        onInstallFinished: logArea.text += success ? "\n✅ Install complete!" : "\n❌ Install failed!"
    }
}
