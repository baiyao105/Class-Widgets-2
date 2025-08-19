import QtQuick
import QtQuick.Controls
import QtQuick as QQ
import QtQuick.Controls as QQC
import QtQuick.Layouts
import QtQuick.Window as QQW
import Widgets
import RinUI
import Debugger
import Windows

QQW.Window {
    id: root
    visible: true
    flags: Qt.FramelessWindowHint | Qt.Window
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

    Row {
        id: widgetsContainer
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 10
        Repeater {
            id: widgetRepeater
            model: WidgetModel

            delegate: Item {
                id: widgetContainer
                width: loader.width
                height: loader.height

                Loader {
                    id: loader
                    source: qmlPath
                    asynchronous: true
                    property int delay

                    onStatusChanged: {
                        if (status === Loader.Ready && item) {
                            if (item && backendObj) item.backend = backendObj
                                Qt.callLater(function() {
                                anim.start()
                            })
                        }
                    }
                }

                SequentialAnimation {
                    id: anim
                    NumberAnimation {
                        target: widgetContainer
                        property: "opacity"
                        from: 0; to: 0; duration: 1
                    }
                    PauseAnimation { duration: index * 125 }
                    ParallelAnimation {
                        NumberAnimation {
                            target: widgetContainer
                            property: "opacity"
                            from: 0; to: 1; duration: 300
                            easing.type: Easing.OutCubic
                        }
                        NumberAnimation {
                            target: widgetContainer;
                            property: "scale";
                            from: 0.8; to: 1; duration: 400;
                            easing.type: Easing.OutBack
                        }
                    }
                }
            }
        }
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
