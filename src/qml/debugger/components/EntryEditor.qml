import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI
import Debugger

Dialog {
    id: dayEditor
    title: "Edit Entry"
    width: 400
    standardButtons: Dialog.Ok | Dialog.Cancel

    property var currentData: ({})  // 用于缓存当前 modelData 副本

    onVisibleChanged: {
        reload(modelData)
    }

    // 保存
    onAccepted: {
        const entryType = typeSegmented.currentIndex === 0 ? "class"
                        : typeSegmented.currentIndex === 1 ? "break"
                        : "activity"

        const startTime = startTimePicker.time.toString("hh:mm")
        const endTime = endTimePicker.time.toString("hh:mm")
        const title = entryTitle.text || undefined
        const id = currentData.id
        const subjectId = entrySubjectId.text || undefined

        console.log("Update entry: " + id)

        AppCentral.scheduleEditor.updateEntry(
            id, entryType,
            startTime, endTime, subjectId, title
        )
    }

    function reload(data) {
        currentData = data || {}
        entryId.text = data.id
        entrySubjectId.text = data.subjectId || ""
        entryTitle.text = data.title || ""

        const type = (data?.type || "class").toLowerCase()
        if (type === "class") typeSegmented.currentIndex = 0
        else if (type === "break") typeSegmented.currentIndex = 1
        else typeSegmented.currentIndex = 2

        startTimePicker.setTime(data.startTime)
        endTimePicker.setTime(data.endTime)
    }

    Segmented {
        id: typeSegmented
        SegmentedItem { text: "Class"; icon.name: "ic_fluent_calendar_20_regular" }
        SegmentedItem { text: "Break"; icon.name: "ic_fluent_clock_sparkle_20_regular" }
        SegmentedItem { text: "Activity"; icon.name: "ic_fluent_shifts_activity_20_regular" }
    }

    RowLayout {
        Text { text: "ID" }
        TextField { Layout.fillWidth: true; id: entryId; readOnly: true }
    }

    RowLayout {
        visible: typeSegmented.currentIndex === 0
        Text { text: "Subject ID" }
        TextField { Layout.fillWidth: true; id: entrySubjectId; }
    }

    RowLayout {
        Text { text: "Title" }
        TextField { Layout.fillWidth: true; id: entryTitle; }
    }

    RowLayout {
        Text { text: "Start Time" }
        Item { Layout.fillWidth: true }
        TimePicker {
            id: startTimePicker
            use24Hour: true
        }
    }
    RowLayout {
        Text { text: "End Time" }
        Item { Layout.fillWidth: true }
        TimePicker {
            id: endTimePicker
            use24Hour: true
        }
    }
}
