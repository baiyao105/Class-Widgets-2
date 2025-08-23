import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI
import Widgets

Widget {
    id: root
    text: qsTr("Current Activity")

    RowLayout {
        anchors.centerIn: parent
        spacing: 10
        Icon {
            icon: AppCentral.scheduleRuntime.currentSubject.icon
                || AppCentral.scheduleRuntime.currentStatus === "free" ? "ic_fluent_accessibility_checkmark_20_regular"
                : "ic_fluent_shifts_activity_20_filled"
            // icon: "ic_fluent_symbols_20_regular"
        }
        Title {
            text: AppCentral.scheduleRuntime.currentEntry.title
                || AppCentral.scheduleRuntime.currentSubject.name || qsTr("Not Set")
        }
    }
}