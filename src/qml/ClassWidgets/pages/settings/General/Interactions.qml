import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI
import Qt5Compat.GraphicalEffects
import ClassWidgets.Components


FluentPage {
    title: qsTr("Interactions")
    // id: generalPage

    ColumnLayout {
        Layout.fillWidth: true
        spacing: 4
        Text {
            typography: Typography.BodyStrong
            text: qsTr("Widgets")
        }

        SettingCard {
            Layout.fillWidth: true
            title: qsTr("Hover Fade")
            description: qsTr(
                "Hover to make the widget transparent and let clicks go through, move away to bring it back."
            )
            icon.name: "ic_fluent_cursor_20_regular"

            Switch {
                id: hoverFadeSwitch
                onCheckedChanged: Configs.set("interactions.hover_fade", checked)
                Component.onCompleted: checked = Configs.data.interactions.hover_fade
            }
        }

        SettingExpander {
            Layout.fillWidth: true
            title: qsTr("Hide Behavior")
            icon.name: "ic_fluent_slide_hide_20_regular"
            description: qsTr("Control when widgets automatically hide")

            SettingItem {
                ColumnLayout {
                    Layout.fillWidth: true
                    RowLayout {
                        Layout.fillWidth: true
                        CheckBox {
                            Layout.fillWidth: true
                            text: qsTr("Hide when clicked")
                        }
                        Text {
                            Layout.fillWidth: true
                            Layout.maximumWidth: 200
                            typography: Typography.Caption
                            color: Colors.proxy.textSecondaryColor
                            horizontalAlignment: Qt.AlignRight
                            text: qsTr("* Widgets won't respond to clicks")
                        }
                    }
                    CheckBox {
                        Layout.fillWidth: true
                        text: qsTr("Hide when in class")
                    }
                    CheckBox {
                        Layout.fillWidth: true
                        text: qsTr("Hide when a window is maximized")
                    }
                    CheckBox {
                        Layout.fillWidth: true
                        text: qsTr("Hide when a window enters fullscreen")
                    }
                }
            }
        }
    }
}