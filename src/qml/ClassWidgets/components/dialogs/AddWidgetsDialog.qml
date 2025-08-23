import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Effects
import RinUI
import Widgets


Dialog {
    id: addWidgetsDialog
    title: qsTr("Add Widgets")
    modal: true
    standardButtons: Dialog.Close
    width: 600
    height: 500

    RowLayout {
        Layout.fillWidth: true
        Layout.fillHeight: true

        ColumnLayout {
            Layout.maximumWidth: 185
            Layout.fillHeight: true
            TextField {
                id: searchField
                placeholderText: qsTr("Search widgets...")
                Layout.fillWidth: true
            }
            ListView {
                id: widgetsListView
                clip: true
                Layout.fillWidth: true
                Layout.fillHeight: true
                model: WidgetsModel.definitionsList
                textRole: "name"
                delegate: ListViewDelegate {
                    leftArea: Icon {
                        icon: "ic_fluent_app_generic_20_regular"
                        size: 22
                    }
                    middleArea: [
                        Text {
                            text: modelData.name
                            elide: Text.ElideRight
                            Layout.fillWidth: true
                        }
                    ]
                }
            }
        }
        ColumnLayout {
            id: widgetInfoLayout
            Layout.fillWidth: true
            Layout.fillHeight: true
            property var model: widgetsListView.model[widgetsListView.currentIndex]

            Item {
                Layout.fillWidth: true
            }

            Text {
                Layout.alignment: Qt.AlignHCenter | Qt.AlignTop
                typography: Typography.Subtitle
                text: widgetInfoLayout.model.name || qsTr("No Widget Selected")
            }

            Item {
                Layout.fillHeight: true
            }

            // 动态加载组件样式
            Loader {
                id: widgetLoader
                Layout.alignment: Qt.AlignCenter
                source: widgetsListView.currentIndex >= 0
                ? widgetInfoLayout.model.qml_path
                : ""
                onItemChanged: {
                    if (item) {
                        if (widgetInfoLayout.model.backend_obj) {
                            item.backend = widgetInfoLayout.model.backend_obj
                        }
                        anim.start()
                    }
                }

                layer.enabled: true
                layer.effect: MultiEffect {
                    shadowEnabled: true
                    shadowColor: Qt.alpha("black", 0.2)
                    shadowBlur: 1
                    shadowVerticalOffset: 4
                }

                ParallelAnimation {
                    id: anim
                    NumberAnimation {
                        target: widgetLoader
                        property: "opacity"
                        from: 0; to: 1; duration: 300
                        easing.type: Easing.OutCubic
                    }
                    NumberAnimation {
                        target: widgetLoader;
                        property: "scale";
                        from: 0.8; to: 1; duration: 400;
                        easing.type: Easing.OutBack
                    }
                }
            }

            Item {
                Layout.fillHeight: true
            }

            Button {
                Layout.alignment: Qt.AlignHCenter | Qt.AlignBottom
                icon.name: "ic_fluent_add_20_regular"
                text: qsTr("Add")
                highlighted: true
                onClicked: {
                    //添加
                    WidgetsModel.addInstance(widgetsListView.model[widgetsListView.currentIndex].id)
                    addWidgetsDialog.close()
                }
            }
        }
    }
}
