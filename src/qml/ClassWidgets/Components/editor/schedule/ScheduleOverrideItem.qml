import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI
import ClassWidgets.Components

/*
 * One editable override row of the course flyout.
 *
 * The row derives its own display text and its week / period choices from the
 * flyout `context` (current week, clicked day, base and effective entries), so
 * the flyout only has to fill the model and react to the signals below.
 */
Item {
    id: root

    required property int index
    required property string entryId
    required property string entryIds
    required property string originalEntryIds
    required property string overrideIds
    required property var weeks

    required property string subjectId
    required property string title
    required property string startTime
    required property string endTime
    required property bool removed
    required property bool expanded
    required property int startPeriod
    required property int endPeriod

    // See ScheduleFlyout.refreshContext().
    property var context: null

    signal toggleRequested()
    signal fieldEdited(string role, var value)
    signal weeksEdited(var value)
    signal periodSelected(string role, int period)
    signal clearRequested()

    readonly property var weeksValue: decodeWeeks(weeks)
    readonly property int cycleCount: context ? context.week.cycle : 1
    readonly property string repeatType: weeksValue === "all"
        ? "all"
        : (Array.isArray(weeksValue) ? "custom" : "round")
    readonly property int repeatValue: Array.isArray(weeksValue)
        ? Number(weeksValue[0] || 1)
        : (typeof weeksValue === "number" ? weeksValue : 1)
    readonly property var customWeeks: {
        const result = []
        for (let i = 0; i < weeksValue.length; ++i) {
            const value = Number(weeksValue[i])
            if (isFinite(value) && value >= 1 && result.indexOf(value) === -1)
                result.push(value)
        }
        result.sort((left, right) => left - right)
        return result
    }

    // Overrides that already claim a week rule for the same entry and day. The
    // row's own records are excluded, so they never block the row itself.
    readonly property var scopes: {
        const result = []
        const contextValue = context
        if (!contextValue)
            return result
        const entryIdsValue = decodeIdList(entryIds)
        const excludedIds = decodeIdList(overrideIds)
        const overrides = contextValue.overrides || []
        for (let i = 0; i < overrides.length; ++i) {
            const item = overrides[i]
            if (entryIdsValue.indexOf(item.entryId) === -1)
                continue
            if (excludedIds.indexOf(item.id) !== -1)
                continue
            const days = Array.isArray(item.dayOfWeek) ? item.dayOfWeek : []
            if (days.length > 0 && days.indexOf(contextValue.week.dayOfWeek) === -1)
                continue
            result.push(item)
        }
        return result
    }

    readonly property bool everyWeekEnabled: {
        for (let i = 0; i < scopes.length; ++i) {
            if (decodeWeeks(scopes[i].weeks) === "all")
                return false
        }
        return true
    }

    readonly property var cycleValues: {
        const used = []
        for (let i = 0; i < scopes.length; ++i) {
            const value = decodeWeeks(scopes[i].weeks)
            if (typeof value === "number" && used.indexOf(value) === -1)
                used.push(value)
        }
        const result = []
        for (let value = 1; value <= cycleCount; ++value) {
            if (used.indexOf(value) === -1)
                result.push(value)
        }
        return result
    }

    // The week-cycle sentence is translated as one string with a {value}
    // placeholder, so translators may move the number (see DayEditor /
    // WeekSelector). The combo box only carries the bare number.
    readonly property string weekCycleFormat: qsTr("Week {value} of every %1 weeks").arg(cycleCount)
    readonly property string weekCyclePrefix: weekCycleFormat.split("{value}")[0]
    readonly property string weekCycleSuffix: weekCycleFormat.split("{value}")[1]
    readonly property string weekFormat: qsTr("Week {value}")
    readonly property string weekPrefix: weekFormat.split("{value}")[0]
    readonly property string weekSuffix: weekFormat.split("{value}")[1]

    readonly property var cycleOptions: {
        const result = []
        for (let i = 0; i < cycleValues.length; ++i) {
            result.push({
                text: cycleCount === 2
                    ? cycleValues[i] === 1 ? qsTr("1") : qsTr("2")
                    : qsTr("%1").arg(cycleValues[i]),
                value: cycleValues[i]
            })
        }
        return result
    }

    readonly property var blockedWeeks: {
        const result = []
        for (let i = 0; i < scopes.length; ++i) {
            const value = decodeWeeks(scopes[i].weeks)
            if (!Array.isArray(value))
                continue
            for (let j = 0; j < value.length; ++j) {
                if (result.indexOf(value[j]) === -1)
                    result.push(value[j])
            }
        }
        return result
    }

    // Periods the row may span: its own periods stay selectable, and so does
    // every empty one, because an override only exists for filled periods.
    readonly property var periodOptions: {
        const options = { start: [], end: [] }
        const contextValue = context
        if (!contextValue)
            return options
        const effectiveEntries = contextValue.effectiveEntries || []
        const available = function(period) {
            const target = effectiveEntries[period - 1]
            if (!target)
                return false
            if (ownsPeriod(target.id))
                return true
            return !target.subjectId && !target.title
        }
        const rangeAvailable = function(from, to) {
            if (from < 1 || to < from || to > effectiveEntries.length)
                return false
            for (let period = from; period <= to; ++period) {
                if (!available(period))
                    return false
            }
            return true
        }
        for (let period = 1; period <= endPeriod; ++period) {
            if (rangeAvailable(period, endPeriod))
                options.start.push(period)
        }
        for (let period = startPeriod; period <= effectiveEntries.length; ++period) {
            if (rangeAvailable(startPeriod, period))
                options.end.push(period)
        }
        return options
    }

    readonly property string displayTitle: title
        || (subjectId && AppCentral.scheduleEditor.subjectNameById(subjectId))
        || (entryForId() && (entryForId().title
            || entryForId().subjectId
                && AppCentral.scheduleEditor.subjectNameById(entryForId().subjectId)))
        || qsTr("Class")

    readonly property string summaryText: weeksLabel + " | " + periodLabel
        + " (" + timeLabel + ")"

    readonly property string weeksLabel: {
        const value = weeksValue
        if (value === "all")
            return qsTr("Every Week")
        if (Array.isArray(value)) {
            return value.length
                ? qsTr("Week %1").arg(value.join(", "))
                : qsTr("Specific Weeks")
        }
        if (cycleCount === 2)
            return Number(value) === 1 ? qsTr("Odd Week") : qsTr("Even Week")
        return qsTr("Week %2 of every %1 weeks").arg(cycleCount).arg(value)
    }

    readonly property string periodLabel: startPeriod === endPeriod
        ? qsTr("Period %1").arg(startPeriod)
        : qsTr("Periods %1-%2").arg(startPeriod).arg(endPeriod)

    readonly property string periodRangeFormat: qsTr("Period {from} to {to}")
    readonly property string periodPrefix: periodRangeFormat.split("{from}")[0]
    readonly property string periodMiddle: periodRangeFormat.split("{from}")[1].split("{to}")[0]
    readonly property string periodSuffix: periodRangeFormat.split("{to}")[1]

    readonly property string timeLabel: {
        const source = entryForId()
        const start = startTime || (source && source.startTime) || "--:--"
        const end = endTime || (source && source.endTime) || "--:--"
        return start + " - " + end
    }

    // Outside the edited week the row is shown, but marked as inactive. Within
    // it, another override on the same entry and day may win: a more specific
    // week rule always wins, and among equally specific rules the later record
    // does.
    readonly property string statusSuffix: {
        const contextValue = context
        if (!contextValue)
            return ""
        const week = contextValue.week
        if (!appliesThisWeek(decodeWeeks(weeks), week))
            return " " + qsTr("(Not This Week)")

        const ids = decodeIdList(overrideIds).filter(value => value !== "")
        if (ids.length === 0)
            return ""

        const overrides = contextValue.overrides || []
        let overriddenCount = 0
        for (let i = 0; i < ids.length; ++i) {
            if (isOverridden(ids[i], week, overrides))
                ++overriddenCount
        }
        if (overriddenCount === ids.length)
            return " " + qsTr("(Overridden)")
        if (overriddenCount > 0)
            return " " + qsTr("(Partially Overridden)")
        return ""
    }

    implicitWidth: removed ? 0 : card.implicitWidth
    width: Math.max(parent ? parent.width : 0, implicitWidth)
    implicitHeight: removed ? 0 : card.implicitHeight
    height: implicitHeight
    visible: !removed

    // ── Helpers ────────────────────────────────────────────────────────
    function decodeWeeks(value) {
        if (Array.isArray(value))
            return value.slice()
        if (typeof value === "number")
            return value
        if (value === "all" || value === null || value === undefined || value === "")
            return "all"
        const text = String(value)
        if (text.charAt(0) === "[") {
            try {
                const parsed = JSON.parse(text)
                return Array.isArray(parsed) ? parsed : "all"
            } catch (error) {
                return "all"
            }
        }
        const number = Number(text)
        return isFinite(number) ? number : "all"
    }

    function decodeIdList(value) {
        if (Array.isArray(value))
            return value.map(item => String(item))
        if (typeof value !== "string" || value.charAt(0) !== "[")
            return []
        try {
            const parsed = JSON.parse(value)
            return Array.isArray(parsed) ? parsed.map(item => String(item)) : []
        } catch (error) {
            return []
        }
    }

    function entryForId() {
        const contextValue = context
        if (!contextValue || !entryId)
            return null
        const effective = contextValue.effectiveEntries || []
        for (let i = 0; i < effective.length; ++i) {
            if (effective[i].id === entryId)
                return effective[i]
        }
        const base = contextValue.baseEntries || []
        for (let i = 0; i < base.length; ++i) {
            if (base[i].id === entryId)
                return base[i]
        }
        return AppCentral.scheduleEditor.getEntry(entryId)
    }

    function ownsPeriod(id) {
        return decodeIdList(entryIds).indexOf(id) !== -1
            || decodeIdList(originalEntryIds).indexOf(id) !== -1
    }

    function appliesThisWeek(value, week) {
        if (value === "all")
            return true
        if (Array.isArray(value))
            return value.indexOf(week.current) !== -1
        const firstWeek = Number(value)
        return isFinite(firstWeek)
            && week.current >= firstWeek
            && (week.current - firstWeek) % week.cycle === 0
    }

    function priorityOf(value) {
        if (Array.isArray(value))
            return 3
        return typeof value === "number" ? 2 : 1
    }

    function isOverridden(overrideId, week, overrides) {
        const contextValue = context
        let targetIndex = -1
        for (let i = 0; i < overrides.length; ++i) {
            if (overrides[i].id === overrideId) {
                targetIndex = i
                break
            }
        }
        if (targetIndex < 0)
            return false

        const target = overrides[targetIndex]
        if (!appliesThisWeek(decodeWeeks(target.weeks), week))
            return false

        const targetPriority = priorityOf(decodeWeeks(target.weeks))
        for (let i = 0; i < overrides.length; ++i) {
            const candidate = overrides[i]
            if (candidate.entryId !== target.entryId)
                continue
            const days = Array.isArray(candidate.dayOfWeek) ? candidate.dayOfWeek : []
            if (days.length > 0 && days.indexOf(contextValue.week.dayOfWeek) === -1)
                continue
            if (!appliesThisWeek(decodeWeeks(candidate.weeks), week))
                continue
            const candidatePriority = priorityOf(decodeWeeks(candidate.weeks))
            if (candidatePriority > targetPriority)
                return true
            if (candidatePriority === targetPriority && i > targetIndex)
                return true
        }
        return false
    }

    function firstAvailableCustomWeek() {
        for (let value = 1; value <= cycleCount; ++value) {
            if (customWeeks.indexOf(value) === -1
                    && blockedWeeks.indexOf(value) === -1)
                return value
        }
        return 0
    }

    Frame {
        id: card
        width: root.width
        topPadding: root.expanded ? 12 : 4
        bottomPadding: root.expanded ? 10 : 8
        leftPadding: 12
        rightPadding: 12

        background: Rectangle {
            radius: 4
            color: summaryButton.pressed
                ? (root.expanded
                    ? Colors.proxy.controlAltQuaternaryColor
                    : Colors.proxy.controlAltTertiaryColor)
                : summaryButton.hovered
                    ? (root.expanded
                        ? Colors.proxy.controlAltTertiaryColor
                        : Colors.proxy.subtleSecondaryColor)
                    : (root.expanded ? Colors.proxy.subtleSecondaryColor : "transparent")
            border.width: root.expanded ? 1 : 0
            border.color: Colors.proxy.controlBorderColor
        }

        contentItem: ColumnLayout {
            id: cardColumn
            spacing: 8

            RowLayout {
                id: summaryRow
                Layout.fillWidth: true
                spacing: 10

                Button {
                    id: summaryButton
                    Layout.fillWidth: true
                    flat: true
                    hoverable: false
                    padding: 0
                    implicitHeight: summaryContent.implicitHeight
                    onClicked: root.toggleRequested()

                    contentItem: ColumnLayout {
                        id: summaryContent
                        spacing: 0
                        Text {
                            Layout.fillWidth: true
                            text: root.displayTitle + root.statusSuffix
                            typography: Typography.BodyStrong
                            opacity: text === qsTr("Class") ? 0.7 : 1  // 当你懒得判断状态的时候be like， 但是确实非常方便硬核（）
                            wrapMode: Text.WordWrap  // 我看看谁能找到这）
                        }
                        Text {
                            Layout.fillWidth: true
                            text: root.summaryText
                            typography: Typography.Caption
                            color: Colors.proxy.textSecondaryColor
                            wrapMode: Text.WordWrap
                        }
                    }
                }

                Button {
                    visible: root.expanded
                    text: qsTr("Clear")
                    onClicked: root.clearRequested()
                }
            }

            ColumnLayout {
                id: settingsColumn
                visible: root.expanded
                Layout.fillWidth: true
                spacing: 4

                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 32
                    spacing: 8
                    Text { text: qsTr("Name") }
                    TextField {
                        Layout.fillWidth: true
                        Layout.minimumWidth: 100
                        text: root.title
                        onTextEdited: root.fieldEdited("title", text)
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8
                    Text { text: qsTr("Subject") }
                    SubjectPickerButton {
                        subjectId: root.subjectId
                        showSubjectIcon: true
                        onSubjectSelected: subjectId => root.fieldEdited("subjectId", subjectId)
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 0

                    ButtonGroup { id: repeatGroup }

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 0
                        RadioButton {
                            Layout.fillWidth: true
                            implicitHeight: 32
                            text: qsTr("Every Week")
                            ButtonGroup.group: repeatGroup
                            checked: root.repeatType === "all"
                            enabled: root.everyWeekEnabled
                            onClicked: root.weeksEdited("all")
                        }
                        RadioButton {
                            Layout.fillWidth: true
                            implicitHeight: 32
                            text: qsTr("Repeat on a Cycle")
                            ButtonGroup.group: repeatGroup
                            checked: root.repeatType === "round"
                            enabled: root.cycleValues.length > 0
                            onClicked: root.weeksEdited(root.cycleValues[0])
                        }
                        RadioButton {
                            Layout.fillWidth: true
                            implicitHeight: 32
                            text: qsTr("Specific Weeks")
                            ButtonGroup.group: repeatGroup
                            checked: root.repeatType === "custom"
                            onClicked: {
                                if (root.customWeeks.length > 0)
                                    return
                                const week = root.firstAvailableCustomWeek()
                                if (week > 0)
                                    root.weeksEdited([week])
                            }
                        }
                    }

                    RowLayout {
                        visible: root.repeatType === "round"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 32
                        spacing: 2
                        Text { text: root.weekCyclePrefix }
                        ComboBox {
                            Layout.fillWidth: true
                            Layout.minimumWidth: 72
                            model: root.cycleOptions
                            textRole: "text"
                            valueRole: "value"
                            currentIndex: root.cycleValues.indexOf(root.repeatValue)
                            onActivated: {
                                if (currentIndex >= 0)
                                    root.weeksEdited(Number(currentValue))
                            }
                        }
                        Text { text: root.weekCycleSuffix }
                    }

                    SpecificWeekEditor {
                        visible: root.repeatType === "custom"
                        Layout.fillWidth: true
                        weeks: root.customWeeks
                        blockedWeeks: root.blockedWeeks
                        onWeeksEdited: value => root.weeksEdited(value)
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 0

                    Text {
                        text: qsTr("Class Time")
                        typography: Typography.Body
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 32
                        spacing: 4
                        Text { text: root.periodPrefix }
                        ComboBox {
                            Layout.fillWidth: true
                            Layout.minimumWidth: 42
                            model: root.periodOptions.start
                            currentIndex: root.periodOptions.start.indexOf(root.startPeriod)
                            onActivated: {
                                if (currentIndex >= 0)
                                    root.periodSelected(
                                        "startTime", Number(model[currentIndex])
                                    )
                            }
                        }
                        Text { text: root.periodMiddle }
                        ComboBox {
                            Layout.fillWidth: true
                            Layout.minimumWidth: 42
                            model: root.periodOptions.end
                            currentIndex: root.periodOptions.end.indexOf(root.endPeriod)
                            onActivated: {
                                if (currentIndex >= 0)
                                    root.periodSelected(
                                        "endTime", Number(model[currentIndex])
                                    )
                            }
                        }
                        Text { text: root.periodSuffix }
                    }
                }

            }
        }
    }
}
