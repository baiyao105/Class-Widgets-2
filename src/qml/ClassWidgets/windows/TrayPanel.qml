import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI


Window {
    id: panel
    title: "Control Panel"
    width: 350
    height: 500
    x: Screen.width / 2 - width / 2
    y: Screen.height / 2 - height / 2
    minimumWidth: width
    maximumWidth: width
    minimumHeight: height
    maximumHeight: height

    minimizeVisible: false
    maximizeVisible: false

    // background
    Rectangle {
        id: appLayer
        width: parent.width
        height: parent.height - bottomRow.height - 10
        color: Theme.currentTheme.colors.layerColor
        border.color: Theme.currentTheme.colors.cardBorderColor
        border.width: 1
        radius: Theme.currentTheme.appearance.windowRadius
    }

    ColumnLayout {
        id: mianlayout
        anchors.fill: parent
        anchors.margins: 14
        anchors.bottomMargin: 4
        spacing: 10

        RowLayout {
            Layout.margins: 4
            spacing: 10
            Image {
                id: logo
                mipmap: true
                source: PathManager.assets("images/logo.png")
                Layout.preferredWidth: 36
                Layout.preferredHeight: 36
            }
            Text {
                typography: Typography.Subtitle
                text: "Class Widgets"
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 4
            SettingCard {
                Layout.fillWidth: true
                icon.name: "ic_fluent_settings_20_regular"
                title: qsTr("Settings")
                description: qsTr("Adjust the settings of Class Widgets")
                Hyperlink {
                    text: "Open"
                    onClicked: AppCentral.openSettings()
                }
            }

            SettingCard {
                Layout.fillWidth: true
                icon.name: "ic_fluent_document_bullet_list_multiple_20_regular"
                title: qsTr("Schedules")
                description: qsTr("Edit your schedule profile")
                Hyperlink {
                    text: "Open"
                }
            }
        }

        Item {
            Layout.fillHeight: true
        }
    }

    RowLayout {
        id: bottomRow
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 4
        Layout.fillWidth: true
        spacing: 0

        ToolButton {
            icon.name: "ic_fluent_developer_board_search_20_regular"
            flat: true
            onClicked: AppCentral.openDebugger()
            ToolTip {
                text: qsTr("Debugger")
                visible: parent.hovered
            }
        }

        ToolButton {
            icon.name: "ic_fluent_info_20_regular"
            flat: true
            ToolTip {
                text: qsTr("About")
                visible: parent.hovered
            }
        }

        ToolButton {
            icon.name: "ic_fluent_arrow_exit_20_regular"
            flat: true
            ToolTip {
                text: qsTr("Exit")
                visible: parent.hovered
            }
            onClicked: AppCentral.quit()
        }
    }


    // connet to AppCentral
    Connections {
        target: AppCentral
        function onTogglePanel(pos) {
            let offsetY = 30
            let x = pos.x - trayPanel.width / 2
            let y = pos.y + offsetY

            if (y + trayPanel.height > trayPanel.Screen.height) {
                y = pos.y - trayPanel.height - offsetY
            }

            if (y < 0) {
                y = 0
            }
            trayPanel.x = x
            trayPanel.y = y

            trayPanel.visible = true
            trayPanel.raise()
            trayPanel.requestActivate()
        }
    }
}