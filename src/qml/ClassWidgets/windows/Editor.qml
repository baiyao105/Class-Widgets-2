import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI
import ClassWidgets.Components


FluentWindow {
    id: settingsWindow
    icon: PathManager.assets("images/icons/cw2_editor.png")
    title: qsTr("Schedule Editor")
    width: Screen.width * 0.6
    height: Screen.height * 0.6
    minimumWidth: 600
    // visible: true
    navigationView.navMinimumExpandWidth: Screen.width
    navigationView.navigationBar.collapsed: true

    onClosing: function(event) {
        event.accepted = false
        settingsWindow.visible = false
    }

    navigationItems: [
        // {
        //     title: qsTr("Dashboard"),
        //     page: PathManager.qml("pages/Home.qml"),
        //     icon: "ic_fluent_board_20_regular",
        // },
        {
            title: qsTr("Home"),
            icon: "ic_fluent_home_20_regular",
            page: PathManager.qml("pages/editor/Home.qml"),
        },
        {
            title: qsTr("Timeline"),
            icon: "ic_fluent_timeline_20_regular",
            page: PathManager.qml("pages/editor/Timeline.qml"),
        },
        {
            title: qsTr("Schedule"),
            icon: "ic_fluent_calendar_20_regular",
            page: PathManager.qml("pages/editor/Schedule.qml"),
        }
        ,
        {
            title: qsTr("Subjects"),
            icon: "ic_fluent_book_20_regular",
            page: PathManager.qml("pages/editor/Subjects.qml"),
        }
    ]

    // 测试水印
    Watermark {
        anchors.centerIn: parent
    }
}