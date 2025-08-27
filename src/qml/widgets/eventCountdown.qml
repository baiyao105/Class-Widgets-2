import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI
import Widgets
import Qt5Compat.GraphicalEffects

Widget {
    id: root
    text: qsTr("Remaining")

    property var countdown: AppCentral.scheduleRuntime.remainingTime || { "minutes": 0, "seconds": 0 }

    ColumnLayout {
        anchors.fill: parent
        spacing: 4

        RowLayout {
            spacing: 0
            Layout.topMargin: -4
            Layout.alignment: Qt.AlignHCenter
            AnimatedDigits {
                id: minute
                value: countdown.minute || "00"
            }
            Title {
                Layout.bottomMargin: font.pixelSize * 0.1
                text: ":"
            }
            AnimatedDigits {
                id: second
                value: (countdown.second + "").padStart(2, "0") || "00"
            }
        }

        ProgressBar {
            id: progressBar
            Layout.fillWidth: true
            Layout.preferredHeight: 4
            value: AppCentral.scheduleRuntime.progress
            primaryColor: {
                switch (AppCentral.scheduleRuntime.currentStatus) {
                    case "free": case "break": return Theme.isDark()? "#46CEA3" : "#2eaa76"
                    case "class": return Theme.isDark()? "#e4a274" : "#dd986f"
                    default: return "#605ed2"
                }
            }
        }
    }
}