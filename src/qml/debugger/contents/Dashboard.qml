import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI
import Debugger


ColumnLayout {
    Layout.fillWidth: true
    Text {
        typography: Typography.BodyStrong
        text: "Dashboard"
    }
    Frame {
        Layout.fillWidth: true
        ColumnLayout {
            width: parent.width

            // ScheduleRuntime
            Text {
                typography: Typography.BodyStrong
                text: "ScheduleRuntime"
            }
            VarStatus {
                Layout.fillWidth: true
                columns: 3
                model: [
                    { name: "currentTime", value: AppCentral.scheduleRuntime.currentTime },
                    {
                        name: "currentDate",
                        value: JSON.stringify(AppCentral.scheduleRuntime.currentDate)   // 显示字典
                    },
                    { name: "currentDayOfWeek", value: AppCentral.scheduleRuntime.currentDayOfWeek },
                    { name: "currentDayEntries", value: AppCentral.scheduleRuntime.currentDayEntries.length,
                        tips: "Only show length of the list"
                    },
                    { name: "currentEntry", value: JSON.stringify(AppCentral.scheduleRuntime.currentEntry) },  // 显示字典
                    { name: "nextEntries", value: JSON.stringify(AppCentral.scheduleRuntime.nextEntries) },
                ]
            }
        }
    }
}