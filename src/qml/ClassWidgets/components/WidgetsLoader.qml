import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window
import RinUI
import Widgets

Flow {
    id: widgetsContainer
    property real scaleFactor: 1
    spacing: 8

    property bool editMode: widgetRepeater.count === 0 ? true : false

    Repeater {
        id: widgetRepeater
        model: WidgetsModel

        delegate: Item {
            id: widgetContainer
            width: loader.width * scaleFactor
            height: loader.height * scaleFactor
            rotation: editMode
            z: dragHandler.active ? 1 : 0
            opacity: dragHandler.active ? 0.5 : 1

            Loader {
                id: loader
                source: model.qmlPath
                asynchronous: true
                anchors.centerIn: parent
                onStatusChanged: {
                    if (status === Loader.Ready) {
                        if (item && model.backendObj) {
                            item.backend = model.backendObj
                        }
                        anim.start()
                    }
                }
                scale: scaleFactor
            }

            ToolButton {
                id: deleteBtn
                visible: widgetsContainer.editMode
                icon.name: "ic_fluent_line_horizontal_1_20_filled"
                size: 12
                width: 24
                height: 24
                anchors.top: parent.top
                anchors.left: parent.left
                onClicked: WidgetsModel.removeWidget(model.instanceId)
            }

            // 拖拽
            DragHandler {
                id: dragHandler
                enabled: widgetsContainer.editMode
                property var originalX: parent.x
                property var originalY: parent.y
                onActiveChanged: {
                    if (active) {
                        originalX = parent.x
                        originalY = parent.y
                    }
                    if (!active) {
                        var from = index
                        var to = Math.round(widgetContainer.x / (widgetContainer.width + widgetsContainer.spacing))
                        if (to < 0) to = 0
                        if (to >= widgetRepeater.count) to = widgetRepeater.count - 1
                        if (to !== from) {
                            WidgetsModel.moveWidget(from, to)
                        } else {
                            x = originalX
                            y = originalY
                        }
                    }
                }
            }

            // 右键菜单
            Menu {
                id: menu
                MenuItem {
                    icon.name: "ic_fluent_column_edit_20_regular"
                    text: qsTr("Edit Widgets Screen")
                    onTriggered: widgetsContainer.editMode = !widgetsContainer.editMode
                }
                MenuItem {
                    icon.name: "ic_fluent_delete_20_regular"
                    text: qsTr("Delete")
                    onTriggered: WidgetsModel.removeWidget(model.instanceId)
                }
            }

            // 鼠标右键打开设置
            TapHandler {
                acceptedButtons: Qt.RightButton
                onTapped: {
                    if (model.settingsQml) {
                        settingsLoader.source = model.settingsQml
                        settingsDialog.open()
                    } else {
                        menu.open()
                    }
                }
            }

            // 动画
            SequentialAnimation on rotation {
                running: widgetsContainer.editMode
                loops: Animation.Infinite
                NumberAnimation { to: 2; duration: 240; easing.type: Easing.InOutQuad }
                NumberAnimation { to: -2; duration: 240; easing.type: Easing.InOutQuad }
            }

            SequentialAnimation {
                id: anim
                NumberAnimation { target: widgetContainer; property: "opacity"; from: 0; to: 0; duration: 1 }
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

            Behavior on opacity {
                NumberAnimation { duration: 100 }
            }
        }
    }

    // 添加小组件&完成
    ColumnLayout {
        visible: widgetsContainer.editMode || widgetRepeater.count === 0
        width: height
        height: widgetRepeater.count > 0 ? widgetRepeater.itemAt(0).height: 100 * scaleFactor

        Button {
            id: addWidgetButton
            Layout.fillWidth: true
            Layout.fillHeight: true

            ColumnLayout {
                anchors.centerIn: parent
                Icon { Layout.alignment: Qt.AlignCenter; name: "ic_fluent_add_20_regular"; size: 18 }
                Text {
                    Layout.alignment: Qt.AlignCenter; text: qsTr("Add");
                    visible: addWidgetButton.height > acceptButton.height
                }
            }

            onClicked: {
                widgetsContainer.editMode = true
                addDialog.open()
            }
        }

        Button {
            visible: widgetsContainer.editMode
            id: acceptButton
            highlighted: true
            Layout.fillWidth: true
            icon.name: "ic_fluent_checkmark_20_regular"
            onClicked: widgetsContainer.editMode = false
        }
    }

    // 添加小组件窗口
    AddWidgetsDialog {
        id: addDialog
    }

    // 小组件设置窗口
    Dialog {
        id: settingsDialog
        title: qsTr("Widget Settings")
        modal: true
        standardButtons: Dialog.Close

        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Loader { id: settingsLoader; }
        }
    }
}
