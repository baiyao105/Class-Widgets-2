import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI


ApplicationWindow {
    id: mainWindow
    title: "Class Widgets Debugger"
    width: 900
    height: 600
    minimumWidth: 425
    minimumHeight: 400
    visible: false

    // color: {
    //     if (Theme.isDark()) {
    //         return "#333"
    //     } else {
    //         return "#eee"
    //     }
    // }

    // notification signal from AppCentral.notification.notify
    Item {
        id: notificationLayer
        property var level: [Severity.Info, Severity.Success, Severity.Warning, Severity.Error]

        Connections {
            target: AppCentral.notification
            onNotify: (icon, level, title, message) => {
                floatLayer.createInfoBar({
                    severity: notificationLayer.level[level],
                    title: title,
                    text: message
                })
            }
        }
    }


    FluentPage {
        anchors.fill: parent
        title: "Edit Schedule"

        
    }
}