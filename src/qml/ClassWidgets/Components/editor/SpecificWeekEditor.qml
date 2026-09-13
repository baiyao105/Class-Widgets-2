import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI

ColumnLayout {
    id: root

    property var weeks: []
    property var blockedWeeks: []
    property int pendingWeek: 1

    signal weeksEdited(var weeks)

    readonly property int maxSpinBoxValue: 2147483647
    readonly property var selectedWeeks: {
        const result = []
        const values = Array.isArray(weeks) ? weeks : []
        for (let i = 0; i < values.length; ++i) {
            const value = Number(values[i])
            if (isFinite(value) && value >= 1 && result.indexOf(value) === -1)
                result.push(value)
        }
        result.sort((left, right) => left - right)
        return result
    }
    readonly property var unavailableWeeks: {
        const result = []
        const append = function(value) {
            const number = Number(value)
            if (!isFinite(number) || number < 1)
                return
            if (result.indexOf(number) === -1)
                result.push(number)
        }
        for (let i = 0; i < selectedWeeks.length; ++i)
            append(selectedWeeks[i])
        const blocked = Array.isArray(blockedWeeks) ? blockedWeeks : []
        for (let i = 0; i < blocked.length; ++i)
            append(blocked[i])
        return result
    }
    readonly property bool canAddWeek: pendingWeek >= 1
        && unavailableWeeks.indexOf(pendingWeek) === -1
    readonly property string weekFormat: qsTr("Week {value}")
    readonly property string weekPrefix: weekFormat.split("{value}")[0]
    readonly property string weekSuffix: weekFormat.split("{value}")[1]

    spacing: 8

    onPendingWeekChanged: syncSpinBox()

    Component.onCompleted: normalizePendingWeek()

    function weekLabel(value) {
        return weekFormat.replace("{value}", String(value))
    }

    function normalizePendingWeek() {
        const current = Number(pendingWeek)
        pendingWeek = isFinite(current)
            ? Math.max(1, Math.min(maxSpinBoxValue, Math.floor(current)))
            : 1
    }

    function nextUnusedWeek(value) {
        let result = Math.max(1, Math.floor(Number(value) || 1))
        const blocked = Array.isArray(blockedWeeks) ? blockedWeeks : []
        while (result < maxSpinBoxValue
                && (selectedWeeks.indexOf(result) !== -1
                    || blocked.indexOf(result) !== -1))
            ++result
        return result
    }

    function addPendingWeek() {
        if (!canAddWeek)
            return

        const result = selectedWeeks.slice()
        result.push(pendingWeek)
        result.sort((left, right) => left - right)
        weeksEdited(result)
        pendingWeek = nextUnusedWeek(pendingWeek + 1)
    }

    function removeWeek(value) {
        const target = Number(value)
        const result = selectedWeeks.filter(week => week !== target)
        weeksEdited(result)
        normalizePendingWeek()
    }

    function syncSpinBox() {
        if (customWeekSpinBox && customWeekSpinBox.value !== pendingWeek)
            customWeekSpinBox.value = pendingWeek
    }

    Flow {
        Layout.fillWidth: true
        spacing: 10
        visible: root.selectedWeeks.length > 0

        Repeater {
            model: root.selectedWeeks

            PillButton {
                text: root.weekLabel(modelData)
                onClicked: root.removeWeek(modelData)
            }
        }
    }

    RowLayout {
        Layout.fillWidth: true
        spacing: 8

        RowLayout {
            spacing: 2
            Text {
                text: root.weekPrefix
            }

            SpinBox {
                id: customWeekSpinBox
                Layout.preferredWidth: 124
                Layout.minimumWidth: 124
                Layout.preferredHeight: 32
                from: 1
                to: root.maxSpinBoxValue
                value: root.pendingWeek
                editable: false
                onValueChanged: {
                    if (value !== root.pendingWeek)
                        root.pendingWeek = value
                }
            }

            Text {
                text: root.weekSuffix
            }
        }

        Item {
            Layout.fillWidth: true
        }

        Button {
            enabled: root.canAddWeek
            onClicked: root.addPendingWeek()
            icon.name: "ic_fluent_add_20_regular"
            text: qsTr("Add")
        }
    }
}