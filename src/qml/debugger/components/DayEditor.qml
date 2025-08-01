import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI
import Debugger

Dialog {
    id: dayEditor
    title: "Edit " + modelData.id
    width: 400
    standardButtons: Dialog.Ok | Dialog.Cancel

    property var currentData: ({})  // 用于缓存当前 modelData 副本

    onVisibleChanged: {
        reload(modelData)
    }

    // 保存
    onAccepted: {
        var id = modelData.id
        var dayOfWeekValue = daySegmented.currentIndex === 0 ? dayOfWeek.currentIndex + 1 : undefined
        var date = daySegmented.currentIndex === 1 ? dayDate.date : undefined

        var weeks
        if (weekCycleTypeAll.checked) {
            weeks = "all"
        } else if (weekCycleTypeRound.checked) {
            weeks = weekCycleRound.value
        } else if (weekCycleTypeCustom.checked) {
            weeks = []
        }

        // 调用 Python 插槽进行更新！
        AppCentral.scheduleEditor.updateDay(id, dayOfWeekValue, weeks, date)
    }

    function reload(data) {
        currentData = data

        // 选择模式
        daySegmented.currentIndex = data.date !== undefined

        // ID
        dayId.text = data.id

        // 日期
        if (data.date)
            dayDate.setDate(data.date)

        // 星期
        dayOfWeek.currentIndex = data.dayOfWeek - 1

        // 周次
        if (data.weeks === "all") {
            weekCycleTypeColumn.children[0].checked = true
        } else if (typeof data.weeks === "number") {
            weekCycleTypeColumn.children[1].checked = true
            weekCycleRound.value = data.weeks
        } else if (typeof data.weeks === "object") {
            weekCycleTypeColumn.children[2].checked = true
        }
    }

    Segmented {
        id: daySegmented
        SegmentedItem { text: "By Week"; icon.name: "ic_fluent_calendar_week_numbers_20_regular" }
        SegmentedItem { text: "By Date"; icon.name: "ic_fluent_calendar_20_regular" }
    }

    RowLayout {
        Text { text: "ID" }
        TextField { Layout.fillWidth: true; id: dayId; readOnly: true }
    }

    RowLayout {
        visible: daySegmented.currentIndex === 1
        Text { text: "Date" }
        Item { Layout.fillWidth: true }
        DatePicker {
            id: dayDate
        }
    }

    ColumnLayout {
        Layout.fillWidth: true
        visible: daySegmented.currentIndex === 0

        RowLayout {
            Text { text: "Day of week" }
            ComboBox {
                id: dayOfWeek
                model: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            }
        }

        RowLayout {
            Text { text: "Week of cycle" }
            Item { Layout.fillWidth: true }
            SpinBox {
                id: weekCycleRound
                visible: weekCycleType.checkedButton.text === "Round"
                from: 1
                to: AppCentral.scheduleEditor.meta.maxWeekCycle
            }
        }

        ButtonGroup { id: weekCycleType; buttons: weekCycleTypeColumn.children }
        Column {
            id: weekCycleTypeColumn
            RadioButton {
                id: weekCycleTypeAll
                text: "All"
            }
            RadioButton {
                id: weekCycleTypeRound
                text: "Round"
            }
            RadioButton {
                id: weekCycleTypeCustom
                text: "Custom"
            }
        }
    }
}
