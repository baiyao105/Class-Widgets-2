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
    width: Screen.width
    height: Screen.height

    property alias editMode: widgetsLoader.editMode

    //background
    Rectangle {
        id: background
        anchors.fill: parent
        visible: opacity > 0
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
            trayPanel.raise()
        }
    }

    WidgetsContainer {
        id: widgetsLoader
        objectName: "widgetsLoader"
        anchors.centerIn: parent
        // onImplicitWidthChanged: if (!root.editMode) root.updateSize()
        // onImplicitHeightChanged: if (!root.editMode) root.updateSize()

        signal geometryChanged()
        onXChanged: geometryChanged()
        onYChanged: geometryChanged()
        onWidthChanged: geometryChanged()
        onHeightChanged: geometryChanged()
        onEditModeChanged: geometryChanged()
        onMenuVisibleChanged: geometryChanged()
    }

    TrayPanel {
        id: trayPanel
    }
}

