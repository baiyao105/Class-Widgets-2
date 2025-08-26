import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI
import Qt5Compat.GraphicalEffects


FluentPage {
    horizontalPadding: 0
    wrapperWidth: width - 42*2

    // Banner / 横幅 //
    contentHeader: Item {
        width: parent.width
        height: Math.max(window.height * 0.35, 200)

        Image {
            id: banner
            anchors.fill: parent
            source: PathManager.assets("images/banner/cw2.png")
            fillMode: Image.PreserveAspectCrop
            // verticalAlignment: Image.AlignTop

            layer.enabled: true
            layer.effect: OpacityMask {
                maskSource: Rectangle {
                    width: banner.width
                    height: banner.height

                    // 渐变效果
                    gradient: Gradient {
                        GradientStop { position: 0.7; color: "white" }  // 不透明
                        GradientStop { position: 1.0; color: "transparent" }  // 完全透明
                    }
                }
            }
        }

        Column {
            anchors {
                top: parent.top
                left: parent.left
                leftMargin: 56
                topMargin: 38
            }
            spacing: 8

            Text {
                color: "#fff"
                typography: Typography.BodyLarge
                text: qsTr("Reimagining Your Schedule.")
            }

            Text {
                color: "#fff"
                typography: Typography.Title
                text: qsTr("Class Widgets 2")
            }
        }
    }

    ColumnLayout {
        Layout.fillWidth: true
        spacing: 4
        Text {
            typography: Typography.BodyStrong
            text: qsTr("Advances")
        }

        SettingCard {
            Layout.fillWidth: true
            icon.name: "ic_fluent_developer_board_search_20_regular"
            title: qsTr("Debug Mode")
            description: qsTr(
                "Enable Debug Mode to , access core widget information, " +
                "and debugging tools. Use with caution—unexpected behavior may occur"
            )

            Switch {
                onCheckedChanged: Configs.set("app.debug_mode", checked)
                Component.onCompleted: checked = Configs.data.app.debug_mode
            }
            // ComboBox {
            //     model: ListModel {
            //         ListElement {
            //             text: qsTr("Pin on Top"); value: "top"
            //         }
            //         ListElement {
            //             text: qsTr("Send to Back"); value: "bottom"
            //         }
            //     }
            //     textRole: "text"
            //
            //     onCurrentIndexChanged: if (focus) Configs.set("preferences.widgets_layer", model.get(currentIndex).value)
            //     Component.onCompleted: {
            //         for (var i = 0; i < model.count; i++) {
            //             if (model.get(i).value === Configs.data.preferences.widgets_layer) {
            //                 currentIndex = i
            //                 break
            //             }
            //         }
            //     }
            // }
        }
    }
}