import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI
import Widgets

Flow {
    id: widgetsContainer
    spacing: 8

    Repeater {
        id: widgetRepeater
        model: WidgetModel

        delegate: Item {
            id: widgetContainer
            width: loader.width
            height: loader.height

            Menu {
                id: menu
                MenuItem {
                    icon.name: "ic_fluent_column_edit_20_regular"
                    text: qsTr("Edit")
                }
                MenuItem {
                    icon.name: "ic_fluent_delete_20_regular"
                    text: qsTr("Delete")
                }
            }

            TapHandler {
                acceptedButtons: Qt.RightButton
                onTapped: menu.open()
            }

            Loader {
                id: loader
                source: qmlPath
                asynchronous: true
                anchors.centerIn: parent
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

    Clip {
        id: addWidgetButton
        width: Math.max(addWidgetButton.childrenRect.width + 2, addWidgetButton.height)
        radius: 12
        height: widgetRepeater.count > 0 ? widgetRepeater.itemAt(0).height : 100
        color: Qt.alpha(backgroundColor , 0.5)

        ColumnLayout {
            anchors.centerIn: parent
            Icon {
                Layout.alignment: Qt.AlignCenter
                name: "ic_fluent_add_20_regular"
            }
            Text {
                Layout.alignment: Qt.AlignCenter
                text: qsTr("Add Widget")
            }
        }
    }
}