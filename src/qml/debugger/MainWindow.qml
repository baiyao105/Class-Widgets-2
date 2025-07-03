import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI


Window {
    id: mainWindow
    title: "Class Widgets Debugger"
    width: 800
    height: 600
    visible: true

    color: {
        if (Theme.isDark) {
            return "#333"
        } else {
            return "#eee"
        }
    }

    FluentPage {
        anchors.fill: parent
        title: "Class Widgets Debugger"

        ColumnLayout {
            Layout.alignment: Qt.AlignHCenter
            Text {
                Layout.alignment: Qt.AlignHCenter
                typography: Typography.Subtitle
                text: "Current Time: " + AppCentral.scheduleRuntime.currentTime
            }
            Text {
                Layout.alignment: Qt.AlignHCenter
                horizontalAlignment: Text.AlignHCenter
                property var date: AppCentral.scheduleRuntime.currentDate
                typography: Typography.Caption
                Layout.fillWidth: true
                text: (
                    "Current Date: " + date.year + "-" + date.month + "-" + date.day + "\n" +
                    "(TimeInformation from Class Widgets -> AppCentral.scheduleRuntime)"
                )
            }
        }

        // 概览
        Overview {}

        // 面板
        Dashboard {}
    }
}