import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI
import ClassWidgets.Components

Dialog {
    id: dayEditor
    modal: true
    width: 500  
    title: currentId ? qsTr("Edit Timeline") : qsTr("New Timeline")

    property string currentId: ""         // 如果有 id = 编辑，否则 = 新建
    property var currentData: ({})        // 临时缓存的数据副本

    // 周循环文案格式
    property int maxWeekCycle: AppCentral.scheduleEditor.meta.maxWeekCycle
    property int roundWeek: 1
    property var customWeeks: []
    property bool canAccept: false
    property bool initialized: false
    onRoundWeekChanged: checkValid()
    onCustomWeeksChanged: {
        checkValid()
        if (weekCycleCustom)
            weekCycleCustom.weeks = customWeeks
    }
    property var roundWeekOptions: []
    property string weekCycleFormat: qsTr("Week {value} of every %1 weeks").arg(maxWeekCycle)
    property string weekCyclePrefix: weekCycleFormat.split("{value}")[0]
    property string weekCycleSuffix: weekCycleFormat.split("{value}")[1]
    property string weekFormat: qsTr("Week {value}")
    property string weekPrefix: weekFormat.split("{value}")[0]
    property string weekSuffix: weekFormat.split("{value}")[1]

    function updateRoundWeekOptions() {
        var options = []
        var cycleLength = Math.max(1, maxWeekCycle)
        for (var i = 1; i <= cycleLength; i++) {
            options.push({
                text: cycleLength === 2
                    ? i === 1 ? qsTr("1") : qsTr("2")
                    : qsTr("%1").arg(i),
                value: i
            })
        }
        roundWeekOptions = options
    }
    function normalizeRoundWeek() {
        var cycleLength = Math.max(1, maxWeekCycle)
        if (roundWeek < 1) {
            roundWeek = 1
        } else if (roundWeek > cycleLength) {
            roundWeek = cycleLength
        }
    }

    function normalizedCustomWeeks(values) {
        var result = []
        var source = Array.isArray(values) ? values : []
        for (var i = 0; i < source.length; i++) {
            var value = Number(source[i])
            if (isFinite(value) && value >= 1
                    && result.indexOf(value) === -1)
                result.push(value)
        }
        result.sort((left, right) => left - right)
        return result
    }

    function normalizeCustomWeeks() {
        customWeeks = normalizedCustomWeeks(customWeeks)
    }

    function firstAvailableCustomWeek() {
        var value = 1
        while (customWeeks.indexOf(value) !== -1)
            value++
        return value
    }

    function setOkEnabled(enabled) {
        if (footer && footer.okButton)
            footer.okButton.enabled = enabled
    }
    onMaxWeekCycleChanged: {
        normalizeRoundWeek()
        normalizeCustomWeeks()
        updateRoundWeekOptions()
    }
    Component.onCompleted: {
        normalizeRoundWeek()
        normalizeCustomWeeks()
        updateRoundWeekOptions()
        initialized = true
        checkValid()
    }

    // 打开方式
    function openFor(data) {
        if (data) {
            currentId = data.id
            reload(data)
        } else {
            currentId = ""
            reload({})   // 新建时重置
        }
        open()
    }

    // 重载数据
    function reload(data) {
        currentData = data || {}
        daySegmented.currentIndex = currentData.date ? 1 : 0
        dayId.text = currentData.id || qsTr("(auto)")

        // 日期
        if (currentData.date) dayDate.selectedDate = currentData.date

        // 星期
        var selectedDays = []
        if (currentData.dayOfWeek !== undefined && currentData.dayOfWeek !== null) {
            if (currentData.dayOfWeek.length !== undefined) {
                for (var i = 0; i < currentData.dayOfWeek.length; i++) {
                    var n = Number(currentData.dayOfWeek[i])
                    if (!isNaN(n) && selectedDays.indexOf(n) === -1)
                        selectedDays.push(n)
                }
            } else {
                var singleDay = Number(currentData.dayOfWeek)
                if (!isNaN(singleDay))
                    selectedDays.push(singleDay)
            }
        }
        selectedDays.sort((left, right) => left - right)
        dayButtons.days = selectedDays

        // 周循环
        weekCycleTypeAll.checked = currentData.weeks === "all" || currentData.weeks === undefined || currentData.weeks === null
        weekCycleTypeRound.checked = typeof currentData.weeks === "number"
        if (weekCycleTypeRound.checked) roundWeek = Number(currentData.weeks)
        weekCycleTypeCustom.checked = Array.isArray(currentData.weeks)
        customWeeks = weekCycleTypeCustom.checked
            ? normalizedCustomWeeks(currentData.weeks)
            : []

        checkValid()
    }

    // 检查是否可以启用 Ok
    function checkValid() {
        if (!initialized)
            return

        var valid = false

        if (daySegmented.currentIndex === 0) {
            // 星期模式
            var hasDaySelected = dayButtons.selectedDays.length > 0
            if (!hasDaySelected) valid = false
            else if (weekCycleTypeAll.checked) valid = true
            else if (weekCycleTypeCustom.checked && customWeeks.length > 0) valid = true
            else if (weekCycleTypeRound.checked && roundWeek >= 1) valid = true
        } else {
            // 日期模式
            valid = !!dayDate.selectedDate
        }

        canAccept = valid
        setOkEnabled(valid)
    }

    ColumnLayout {
        spacing: 24
        Layout.fillWidth: true

        Segmented {
            id: daySegmented
            Layout.fillWidth: true
            onCurrentIndexChanged: checkValid()
            SegmentedItem { text: qsTr("By Week"); icon.name: "ic_fluent_calendar_week_numbers_20_regular" }
            SegmentedItem { text: qsTr("By Date"); icon.name: "ic_fluent_calendar_20_regular" }
        }

        RowLayout {
            Text { text: qsTr("ID"); width: 100 }
            TextField { id: dayId; Layout.fillWidth: true; readOnly: true;}
            visible: false
        }

        RowLayout {
            visible: daySegmented.currentIndex === 1
            Text { text: qsTr("Date"); width: 100 }

            Item { Layout.fillWidth: true }

            CalendarDatePicker {
                id: dayDate
                onSelectedDateChanged: checkValid()
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 12
            visible: daySegmented.currentIndex === 0

            ColumnLayout {
                spacing: 6
                Text { text: qsTr("Days of Week") }

                WeekdaySelector {
                    id: dayButtons
                    Layout.fillWidth: true
                    onSelectionChanged: dayEditor.checkValid()
                }
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 6
                Text { text: qsTr("Week")}

                RowLayout {
                    id: weekCycleTypeColumn
                    spacing: 12
                    RadioButton { id: weekCycleTypeAll; text: qsTr("Every Week"); onCheckedChanged: dayEditor.checkValid() }
                    RadioButton { id: weekCycleTypeRound; text: qsTr("Repeat on a Cycle"); onCheckedChanged: dayEditor.checkValid() }
                    RadioButton {
                        id: weekCycleTypeCustom
                        text: qsTr("Specific Weeks")
                        onCheckedChanged: dayEditor.checkValid()
                        onClicked: {
                            if (dayEditor.customWeeks.length > 0)
                                return
                            const week = dayEditor.firstAvailableCustomWeek()
                            if (week > 0)
                                dayEditor.customWeeks = [week]
                        }
                    }
                }

                RowLayout {
                    visible: weekCycleTypeRound.checked
                    spacing: 2
                    Text { text: weekCyclePrefix }
                    ComboBox {
                        id: weekCycleRound
                        model: dayEditor.roundWeekOptions
                        Layout.preferredWidth: 72
                        textRole: "text"
                        valueRole: "value"
                        currentIndex: Math.max(0, dayEditor.roundWeek - 1)
                        onActivated: dayEditor.roundWeek = currentIndex + 1
                    }
                    Text { text: weekCycleSuffix }
                }

                SpecificWeekEditor {
                    id: weekCycleCustom
                    visible: weekCycleTypeCustom.checked
                    Layout.fillWidth: true
                    onWeeksEdited: value => dayEditor.customWeeks = value
                }
            }
        }
    }

    footer: DialogButtonBox {
        standardButtons: DialogButtonBox.Ok | DialogButtonBox.Cancel
        property Button okButton: standardButton(DialogButtonBox.Ok)

        onAccepted: {
            var dayOfWeekValue = []
            var date = ""
            var weeks = undefined

            if (daySegmented.currentIndex === 0) {
                // 星期模式
                dayOfWeekValue = dayButtons.selectedDays.slice()
                if (weekCycleTypeAll.checked) {
                    weeks = "all"
                } else if (weekCycleTypeRound.checked) {
                    weeks = roundWeek
                } else if (weekCycleTypeCustom.checked) {
                    weeks = customWeeks.slice()
                }
            } else {
                // 日期模式
                date = dayDate.selectedDate
                weeks = "all"
            }

            if (currentId) {
                AppCentral.scheduleEditor.updateDay(currentId, dayOfWeekValue, weeks, date)
            } else {
                AppCentral.scheduleEditor.addDay(dayOfWeekValue, weeks, date)
            }
        }
        onRejected: dayEditor.close()

        Component.onCompleted: {
            Qt.callLater(function() {
                dayEditor.setOkEnabled(dayEditor.canAccept)
            })
        }
    }
}
