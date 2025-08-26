import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI


FluentWindow {
    id: settingsWindow
    icon: PathManager.assets("images/icons/cw2_settings.png")
    title: qsTr("Settings")
    width: Screen.width * 0.5
    height: Screen.height * 0.6
    minimumWidth: 600
    visible: true

    onClosing: function(event) {
        event.accepted = false
        settingsWindow.visible = false
    }

    Component.onCompleted: {
        y = 700
    }

    navigationItems: [
        {
            title: qsTr("Dashboard"),
            page: PathManager.qml("pages/Dashboard.qml"),
            icon: "ic_fluent_board_20_regular",
        },
        {
            title: qsTr("General"),
            icon: "ic_fluent_apps_settings_20_regular",
            page: PathManager.qml("pages/general/index.qml"),
            subItems: [
                {
                    title: qsTr("Widgets"),
                    page: PathManager.qml("pages/general/Widgets.qml"),
                    icon: "ic_fluent_apps_20_regular"
                }
            ]
        },
        {
            title: qsTr("About"),
            page: PathManager.qml("pages/About.qml"),
            icon: "ic_fluent_info_20_regular",
        },
    ]
}