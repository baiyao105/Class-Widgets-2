import QtQuick
import QtQuick.Controls
import QtQuick as QQ
import QtQuick.Controls as QQC
import QtQuick.Layouts
import QtQuick.Window as QQW
import Widgets
import RinUI
import ClassWidgets.Components
import ClassWidgets.Windows

QQW.Window {
    id: root
    visible: true
    flags: Qt.FramelessWindowHint | Qt.Tool
    color: "transparent"

    property alias editMode: widgetsLoader.editMode

    function updateSize() {
        if (editMode) {
            root.x = 0
            root.y = 0
            root.width = Screen.width
            root.height = Screen.height
        } else {
            root.width = Math.min(widgetsLoader.implicitWidth, Screen.width)
            root.height = widgetsLoader.implicitHeight
            root.x = Math.max(0, (Screen.width - root.width) / 2)
            root.y = Math.max(0, (Screen.height - root.height) / 2)
        }
    }

    //background
    Rectangle {
        id: background
        anchors.fill: parent
        color: "black"
        opacity: editMode? 0.25 : 0
        Behavior on opacity {
            NumberAnimation {
                duration: 200
                easing.type: Easing.InOutQuad
            }
        }
    }

    Connections {
        target: AppCentral
        function onTogglePanel(pos) {
            root.raise()
        }
    }

    WidgetsLoader {
        id: widgetsLoader
        anchors.centerIn: parent
        onImplicitWidthChanged: if (!root.editMode) root.updateSize()
        onImplicitHeightChanged: if (!root.editMode) root.updateSize()
    }

    TrayPanel {
        id: trayPanel
    }

    Component.onCompleted: updateSize()

    onEditModeChanged: updateSize()
}

