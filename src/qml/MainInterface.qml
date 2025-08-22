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
    // width: Screen.width
    // height: Screen.height
    width: 1200
    height: 200
    color: "transparent"

    Connections {
        target: AppCentral
        function onTogglePanel(pos) {
            root.raise()
        }
    }

    WidgetsLoader {
        anchors.horizontalCenter: parent.horizontalCenter
    }

    // Button {
    //     anchors.left: parent.left
    //     anchors.top: parent.top
    //
    //     text: "Widgets: " + JSON.stringify(WidgetModel.enabledWidgets)
    //     onClicked: presetEditor.visible = true
    // }
    //
    //
    // WidgetsEditor {
    //     id: presetEditor
    // }

    TrayPanel {
        id: trayPanel
    }
}
