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

    property bool initialized: false
    property alias editMode: widgetsLoader.editMode

    //background
    Rectangle {
        id: background
        anchors.fill: parent
        visible: editMode
        color: "black"
        opacity: editMode? 0.25 : 0
        Behavior on opacity {
            NumberAnimation {
                duration: 200
                easing.type: Easing.InOutQuad
            }
        }
    }

    Timer {
        id: initalizeTimer
        interval: 300
        running: true
        repeat: false
        onTriggered: root.initialized = true
    }

    MouseArea {
        anchors.fill: parent
        onClicked: {
            if (widgetsLoader.menuVisible) {
                widgetsLoader.menuVisible = false
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
        // anchors.centerIn: parent
        // x: (parent.width - width) / 2
        // y: (parent.height - height) / 2
        property var preferences: Configs.data.preferences

        // 计算位置
        function calcX() {
            switch (preferences.widgets_anchor) {
            case "top_left":
            case "bottom_left":
                return preferences.widgets_offset_x;
            case "top_center":
            case "bottom_center":
                return (parent.width - width) / 2 + preferences.widgets_offset_x;
            case "top_right":
            case "bottom_right":
                return parent.width - width - preferences.widgets_offset_x;
            }
            return 0;
        }

        function calcY() {
            switch (preferences.widgets_anchor) {
            case "top_left":
            case "top_center":
            case "top_right":
                return preferences.widgets_offset_y;
            case "bottom_left":
            case "bottom_center":
            case "bottom_right":
                return parent.height - height - preferences.widgets_offset_y;
            }
            return (parent.height - height) / 2 + preferences.widgets_offset_y;
        }

        x: calcX()
        y: calcY()

        Behavior on x { NumberAnimation { duration: 300 * root.initialized; easing.type: Easing.OutQuint } }
        Behavior on y { NumberAnimation { duration: 300 * root.initialized; easing.type: Easing.OutQuint } }

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

