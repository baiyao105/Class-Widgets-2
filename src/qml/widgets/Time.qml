import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI
import Widgets

Widget {
    id: root
    text: qsTr("time")
    property var dateTime: {
        "hour": 0,
        "minute": 0,
        "second": 0
    }

    RowLayout {
        anchors.centerIn: parent
        spacing: 0
        AnimatedDigits {
            id: hour
            value: dateTime.hour || "00"
        }
        Title {
            y: -5
            text: ":"
        }
        AnimatedDigits {
            id: minute
            value: dateTime.minute || "00"
        }
        Title {
            y: -5
            text: ":"
        }
        AnimatedDigits {
            id: second
            value: dateTime.second || "00"
        }

        Timer {
            interval: 500
            running: true
            repeat: true
            onTriggered: {
                dateTime = backend.getDateTime()
            }
        }
    }

    Component.onCompleted: {
        Qt.callLater(function() {
            dateTime = backend.getDateTime()
        })
    }
}