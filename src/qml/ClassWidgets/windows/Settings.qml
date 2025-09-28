import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI
import ClassWidgets.Components


FluentWindow {
    id: settingsWindow
    icon: PathManager.assets("images/icons/cw2_settings.png")
    title: qsTr("Settings")
    width: Screen.width * 0.5
    height: Screen.height * 0.6
    minimumWidth: 600
    // visible: true

    onClosing: function(event) {
        event.accepted = false
        settingsWindow.visible = false
    }

    navigationItems: [
        {
            title: qsTr("Dashboard"),
            page: PathManager.qml("pages/settings/Dashboard.qml"),
            icon: "ic_fluent_board_20_regular",
        },
        {
            title: qsTr("General"),
            icon: "ic_fluent_apps_settings_20_regular",
            page: PathManager.qml("pages/settings/general/index.qml"),
            subItems: [
                {
                    title: qsTr("Widgets"),
                    page: PathManager.qml("pages/settings/general/widgets.qml"),
                    icon: "ic_fluent_apps_20_regular"
                }
            ]
        },
        {
            title: qsTr("About"),
            page: PathManager.qml("pages/settings/About.qml"),
            icon: "ic_fluent_info_20_regular",
        },
    ]

    // 测试水印
    Watermark {
        anchors.centerIn: parent
    }
}