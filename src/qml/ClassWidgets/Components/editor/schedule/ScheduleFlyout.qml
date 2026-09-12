import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI

Flyout {
    id: root

    property var entry: null
    property var selectedCell: null
    property var weekSelector: null
    property int overridesRevision: AppCentral.scheduleEditor.overridesRevision
    property bool syncing: false
    property var baseDayEntries: []
    property var effectiveDayEntries: []

    readonly property real overlayWidth: Overlay.overlay ? Overlay.overlay.width : 0
    readonly property real overlayHeight: Overlay.overlay ? Overlay.overlay.height : 0
    readonly property real popupMaxHeight: overlayHeight > 0
        ? Math.max(240, overlayHeight - 32)
        : 720
    readonly property int maxListHeight: Math.max(120, Math.floor(popupMaxHeight - 220))

    readonly property real popupMinWidth: 320
    readonly property real popupPreferredWidth: contentColumn.implicitWidth + leftPadding + rightPadding

    implicitWidth: overlayWidth > 0
        ? Math.max(popupMinWidth, Math.min(popupPreferredWidth, overlayWidth - 32))
        : Math.max(popupMinWidth, popupPreferredWidth)
    implicitHeight: Math.min(contentColumn.implicitHeight + topPadding + bottomPadding, popupMaxHeight)
    width: implicitWidth
    height: implicitHeight
    padding: 16
    leftPadding: 16
    rightPadding: 16
    position: Position.Right

    ListModel {
        id: overrideModel
    }

    onAboutToShow: reloadOverrides()
    onEntryChanged: reloadOverrides()
    onOverridesRevisionChanged: if (!syncing) reloadOverrides()
    // ── Data normalization ─────────────────────────────────────────────
    function sameValue(left, right) {
        return JSON.stringify(left) === JSON.stringify(right)
    }


    function encodeDays(value) {
        return JSON.stringify((value || []).map(item => Number(item)))
    }

    function decodeDays(value) {
        if (Array.isArray(value))
            return value.map(item => Number(item))
        if (typeof value === "string" && value.charAt(0) === "[") {
            try {
                const parsed = JSON.parse(value)
                return Array.isArray(parsed) ? parsed.map(item => Number(item)) : []
            } catch (error) {
                return []
            }
        }
        return []
    }
    function encodeWeeks(value) {
        if (value === "all" || value === null || value === undefined || value === "")
            return "all"
        if (Array.isArray(value))
            return JSON.stringify(value.map(item => Number(item)))
        const number = Number(value)
        return isFinite(number) ? String(number) : "all"
    }

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

    // ── Schedule context ───────────────────────────────────────────────
    function cycleCount() {
        return Math.max(1, Number(weekSelector ? weekSelector.maxWeekCycle : 1) || 1)
    }

    function currentWeek() {
        return Math.max(1, Number(weekSelector ? weekSelector.currentWeek : 1) || 1)
    }

    function selectedDayOfWeek() {
        const column = Number(selectedCell ? selectedCell.column : -1)
        if (!isFinite(column) || column < 0)
            return []
        // ScheduleTableView columns: Sunday, Monday ... Saturday.
        // Schedule data: Monday=1 ... Sunday=7.
        return [(column + 6) % 7 + 1]
    }

    function entryDayForId(entryId) {
        const days = AppCentral.scheduleEditor.entriesData || []
        for (const day of days) {
            for (const item of (day.entries || [])) {
                if (item.id === entryId)
                    return day
            }
        }
        return null
    }

    function refreshContext() {
        const entryId = entry ? (entry.id || "") : ""
        const day = entryId ? entryDayForId(entryId) : null
        baseDayEntries = day
            ? (day.entries || []).filter(item => item.type === "class")
            : []

        const columns = AppCentral.scheduleEditor.getEffectiveEntries(currentWeek()) || []
        const column = Number(selectedCell ? selectedCell.column : -1)
        effectiveDayEntries = column >= 0 && column < columns.length
            ? (columns[column] || [])
            : []
    }

    function classEntriesForId(entryId) {
        if (!entryId || baseDayEntries.length === 0)
            return baseDayEntries
        for (const item of baseDayEntries) {
            if (item.id === entryId)
                return baseDayEntries
        }
        const day = entryDayForId(entryId)
        if (!day || !day.entries)
            return []
        return day.entries.filter(item => item.type === "class")
    }

    function basePeriodForId(entryId) {
        const items = classEntriesForId(entryId)
        for (let i = 0; i < items.length; ++i) {
            if (items[i].id === entryId)
                return i + 1
        }
        const row = Number(selectedCell ? selectedCell.row : -1)
        return isFinite(row) && row >= 0 ? row + 1 : 1
    }

    function baseEndPeriodForId(entryId) {
        const fallback = basePeriodForId(entryId)
        const source = entryForId(entryId)
        return endPeriodForTime(entryId, source ? source.endTime : "", fallback)
    }

    function periodCountForId(entryId) {
        return Math.max(1, classEntriesForId(entryId).length)
    }

    function periodForTime(entryId, time, fallback) {
        if (!time)
            return fallback
        const items = classEntriesForId(entryId)
        for (let i = 0; i < items.length; ++i) {
            if (items[i].startTime === time)
                return i + 1
        }
        for (let i = 0; i < items.length; ++i) {
            if (time >= items[i].startTime && time < items[i].endTime)
                return i + 1
        }
        return fallback
    }

    function endPeriodForTime(entryId, time, fallback) {
        if (!time)
            return fallback
        const items = classEntriesForId(entryId)
        for (let i = 0; i < items.length; ++i) {
            if (items[i].endTime === time)
                return i + 1
        }
        for (let i = 0; i < items.length; ++i) {
            if (time > items[i].startTime && time <= items[i].endTime)
                return i + 1
        }
        return fallback
    }

    function startTimeForPeriod(entryId, period) {
        const items = classEntriesForId(entryId)
        const item = items[Math.max(0, Number(period) - 1)]
        return item ? (item.startTime || "") : ""
    }

    function endTimeForPeriod(entryId, period) {
        const items = classEntriesForId(entryId)
        const item = items[Math.max(0, Number(period) - 1)]
        return item ? (item.endTime || "") : ""
    }

    function entryForId(entryId) {
        for (const item of effectiveDayEntries) {
            if (item.id === entryId)
                return item
        }
        for (const item of baseDayEntries) {
            if (item.id === entryId)
                return item
        }
        return AppCentral.scheduleEditor.getEntry(entryId)
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

    function overrideGroupKey(item) {
        return encodeDays(item.dayOfWeek || []) + "|"
            + encodeWeeks(item.weeks) + "|"
            + String(item.subjectId || "") + "|"
            + String(item.title || "")
    }

    function overridesForEntryOnDay(entryId, dayOfWeek) {
        const result = []
        for (const item of (AppCentral.scheduleEditor.overrides || [])) {
            if (item.entryId === entryId && overrideMatchesDay(item, dayOfWeek))
                result.push(item)
        }
        return result
    }

    function recordWithSignature(records, key) {
        for (const item of records) {
            if (overrideGroupKey(item) === key)
                return item
        }
        return null
    }

    function appendOverrideGroup(group) {
        if (!group || group.start < 0 || group.records.length === 0)
            return
        const firstEntry = baseDayEntries[group.start]
        const lastEntry = baseDayEntries[group.end]
        const firstOverride = group.records[0]
        const lastOverride = group.records[group.records.length - 1]
        if (!firstEntry || !lastEntry)
            return

        const entryIds = []
        const overrideIds = []
        for (let i = group.start; i <= group.end; ++i) {
            entryIds.push(baseDayEntries[i].id)
            const override = group.records[i - group.start]
            overrideIds.push(override ? (override.id || "") : "")
        }

        overrideModel.append({
            id: firstOverride.id || "",
            entryId: firstEntry.id,
            entryIds: JSON.stringify(entryIds),
            originalEntryIds: JSON.stringify(entryIds),
            overrideIds: JSON.stringify(overrideIds),
            dayOfWeek: encodeDays(firstOverride.dayOfWeek || []),
            weeks: encodeWeeks(firstOverride.weeks),
            subjectId: firstOverride.subjectId || "",
            title: firstOverride.title || "",
            startTime: firstEntry.startTime || "",
            endTime: lastEntry.endTime || "",
            originalDayOfWeek: encodeDays(firstOverride.dayOfWeek || []),
            originalWeeks: encodeWeeks(firstOverride.weeks),
            startPeriod: group.start + 1,
            endPeriod: group.end + 1,
            isDraft: false,
            removed: false,
            expanded: false
        })
    }

    function collapseAllOverrides() {
        for (let i = 0; i < overrideModel.count; ++i)
            overrideModel.setProperty(i, "expanded", false)
    }

    function toggleOverride(index) {
        const item = overrideModel.get(index)
        if (!item)
            return
        const expand = !item.expanded
        collapseAllOverrides()
        overrideModel.setProperty(index, "expanded", expand)
    }

    function entryIdsForRange(startPeriod, endPeriod) {
        const result = []
        for (let period = startPeriod; period <= endPeriod; ++period) {
            const target = baseDayEntries[period - 1]
            if (target)
                result.push(target.id)
        }
        return result
    }

    function itemEntryIds(item) {
        return decodeIdList(item ? item.entryIds : "[]")
    }

    function itemOriginalEntryIds(item) {
        return decodeIdList(item ? item.originalEntryIds : "[]")
    }

    function itemOverrideIds(item) {
        return decodeIdList(item ? item.overrideIds : "[]")
    }

    function isOwnedPeriod(item, entryId) {
        return itemEntryIds(item).indexOf(entryId) !== -1
            || itemOriginalEntryIds(item).indexOf(entryId) !== -1
    }

    function isPeriodAvailable(item, period) {
        const target = effectiveDayEntries[period - 1]
        if (!target)
            return false
        if (isOwnedPeriod(item, target.id))
            return true
        return !target.subjectId && !target.title
    }

    function isRangeAvailable(item, startPeriod, endPeriod) {
        if (startPeriod < 1 || endPeriod < startPeriod || endPeriod > effectiveDayEntries.length)
            return false
        for (let period = startPeriod; period <= endPeriod; ++period) {
            if (!isPeriodAvailable(item, period))
                return false
        }
        return true
    }

    function startPeriodOptionsForItem(startPeriodValue, endPeriodValue, entryIdsValue, originalEntryIdsValue) {
        const result = []
        const item = {
            startPeriod: startPeriodValue,
            endPeriod: endPeriodValue,
            entryIds: entryIdsValue,
            originalEntryIds: originalEntryIdsValue
        }
        for (let period = 1; period <= endPeriodValue; ++period) {
            if (isRangeAvailable(item, period, endPeriodValue))
                result.push(period)
        }
        return result
    }

    function endPeriodOptionsForItem(startPeriodValue, endPeriodValue, entryIdsValue, originalEntryIdsValue) {
        const result = []
        const item = {
            startPeriod: startPeriodValue,
            endPeriod: endPeriodValue,
            entryIds: entryIdsValue,
            originalEntryIds: originalEntryIdsValue
        }
        for (let period = startPeriodValue; period <= effectiveDayEntries.length; ++period) {
            if (isRangeAvailable(item, startPeriodValue, period))
                result.push(period)
        }
        return result
    }

    function applyPeriodSelection(index, role, period) {
        const item = overrideModel.get(index)
        const selectedPeriod = Number(period)
        if (!item || !isFinite(selectedPeriod))
            return
        let startPeriod = item.startPeriod
        let endPeriod = item.endPeriod
        if (role === "startTime") {
            startPeriod = Math.min(selectedPeriod, endPeriod)
        } else {
            endPeriod = Math.max(selectedPeriod, startPeriod)
        }
        if (!isRangeAvailable(item, startPeriod, endPeriod))
            return

        const entryIds = entryIdsForRange(startPeriod, endPeriod)
        if (entryIds.length === 0)
            return
        const firstEntry = baseDayEntries[startPeriod - 1]
        const lastEntry = baseDayEntries[endPeriod - 1]
        overrideModel.setProperty(index, "entryId", entryIds[0])
        overrideModel.setProperty(index, "entryIds", JSON.stringify(entryIds))
        overrideModel.setProperty(index, "startPeriod", startPeriod)
        overrideModel.setProperty(index, "endPeriod", endPeriod)
        overrideModel.setProperty(index, "startTime", firstEntry ? (firstEntry.startTime || "") : "")
        overrideModel.setProperty(index, "endTime", lastEntry ? (lastEntry.endTime || "") : "")
    }

    function repeatTypeFor(weeks) {
        if (weeks === "all" || weeks === null || weeks === undefined || weeks === "")
            return "all"
        return Array.isArray(weeks) ? "custom" : "round"
    }

    function cycleName(value) {
        const number = Math.max(1, Number(value) || 1)
        if (cycleCount() === 2)
            return number === 1 ? qsTr("Odd") : qsTr("Even")
        return qsTr("Week %1").arg(number)
    }

    function cycleOptions() {
        const result = []
        for (let i = 1; i <= cycleCount(); ++i)
            result.push(cycleName(i))
        return result
    }

    function cycleOptionsForValues(values) {
        const result = []
        for (const value of values)
            result.push(cycleName(value))
        return result
    }

    function overrideMatchesDay(item, dayOfWeek) {
        if (!item)
            return false
        const days = Array.isArray(item.dayOfWeek)
            ? item.dayOfWeek.map(value => Number(value))
            : []
        return days.length === 0 || days.indexOf(dayOfWeek) !== -1
    }

    function existingScopesForItem(entryIdsValue, dayOfWeek, overrideIdsValue) {
        const entryIds = decodeIdList(entryIdsValue)
        const excludedIds = decodeIdList(overrideIdsValue)
        const result = []
        for (const item of (AppCentral.scheduleEditor.overrides || [])) {
            if (entryIds.indexOf(item.entryId) === -1)
                continue
            if (excludedIds.indexOf(item.id) !== -1)
                continue
            if (!overrideMatchesDay(item, dayOfWeek))
                continue
            result.push(item)
        }
        return result
    }

    function everyWeekOptionEnabled(entryIdsValue, dayOfWeek, overrideIdsValue) {
        const scopes = existingScopesForItem(entryIdsValue, dayOfWeek, overrideIdsValue)
        for (const item of scopes) {
            if (decodeWeeks(item.weeks) === "all")
                return false
        }
        return true
    }

    function cycleValuesForItem(entryIdsValue, dayOfWeek, overrideIdsValue) {
        const scopes = existingScopesForItem(entryIdsValue, dayOfWeek, overrideIdsValue)
        const used = []
        for (const item of scopes) {
            const value = decodeWeeks(item.weeks)
            if (typeof value === "number" && used.indexOf(value) === -1)
                used.push(value)
        }
        const result = []
        for (let value = 1; value <= cycleCount(); ++value) {
            if (used.indexOf(value) === -1)
                result.push(value)
        }
        return result
    }

    function blockedCustomWeeks(entryIdsValue, dayOfWeek, overrideIdsValue) {
        const scopes = existingScopesForItem(entryIdsValue, dayOfWeek, overrideIdsValue)
        const result = []
        for (const item of scopes) {
            const value = decodeWeeks(item.weeks)
            if (!Array.isArray(value))
                continue
            for (const week of value) {
                if (result.indexOf(week) === -1)
                    result.push(week)
            }
        }
        return result
    }

    function defaultWeeksForNewItem(entryIdsValue, dayOfWeek) {
        if (everyWeekOptionEnabled(entryIdsValue, dayOfWeek, "[]"))
            return "all"

        const cycleValues = cycleValuesForItem(entryIdsValue, dayOfWeek, "[]")
        if (cycleValues.length > 0)
            return cycleValues[0]

        const blocked = blockedCustomWeeks(entryIdsValue, dayOfWeek, "[]")
        let week = currentWeek()
        while (blocked.indexOf(week) !== -1)
            ++week
        return [week]
    }

    function weeksLabel(weeks) {
        if (weeks === "all" || weeks === null || weeks === undefined || weeks === "")
            return qsTr("Every Week")
        if (Array.isArray(weeks)) {
            return weeks.length
                ? qsTr("Week %1").arg(weeks.join(", "))
                : qsTr("Every Week")
        }
        if (cycleCount() === 2)
            return Number(weeks) === 1 ? qsTr("Odd Week") : qsTr("Even Week")
        return qsTr("Week %2 of every %1 weeks").arg(cycleCount()).arg(weeks)
    }

    function overrideAppliesThisWeek(weeks) {
        const decoded = decodeWeeks(weeks)
        if (decoded === "all" || decoded === null || decoded === undefined || decoded === "")
            return true
        if (Array.isArray(decoded))
            return decoded.indexOf(currentWeek()) !== -1
        const firstWeek = Number(decoded)
        return isFinite(firstWeek)
            && currentWeek() >= firstWeek
            && (currentWeek() - firstWeek) % cycleCount() === 0
    }

    function overridePriorityValue(weeks) {
        const decoded = decodeWeeks(weeks)
        if (Array.isArray(decoded))
            return 3
        if (typeof decoded === "number")
            return 2
        return 1
    }

    function overrideRecordIsOverridden(overrideId, dayOfWeek) {
        const overrides = AppCentral.scheduleEditor.overrides || []
        let targetIndex = -1
        for (let i = 0; i < overrides.length; ++i) {
            if (overrides[i].id === overrideId) {
                targetIndex = i
                break
            }
        }
        if (targetIndex < 0 || !overrideAppliesThisWeek(overrides[targetIndex].weeks))
            return false

        const target = overrides[targetIndex]
        const targetPriority = overridePriorityValue(target.weeks)
        for (let i = 0; i < overrides.length; ++i) {
            const candidate = overrides[i]
            if (candidate.entryId !== target.entryId)
                continue
            if (!overrideMatchesDay(candidate, dayOfWeek))
                continue
            if (!overrideAppliesThisWeek(candidate.weeks))
                continue
            const candidatePriority = overridePriorityValue(candidate.weeks)
            if (candidatePriority > targetPriority)
                return true
            if (candidatePriority === targetPriority && i > targetIndex)
                return true
        }
        return false
    }

    function overrideStatusSuffix(overrideIdsValue, weeks, dayOfWeek) {
        if (!overrideAppliesThisWeek(weeks))
            return " " + qsTr("(Not This Week)")

        const overrideIds = decodeIdList(overrideIdsValue).filter(value => value !== "")
        if (overrideIds.length === 0)
            return ""

        let overriddenCount = 0
        for (const overrideId of overrideIds) {
            if (overrideRecordIsOverridden(overrideId, dayOfWeek))
                ++overriddenCount
        }
        if (overriddenCount === overrideIds.length)
            return " " + qsTr("(Overridden)")
        if (overriddenCount > 0)
            return " " + qsTr("(Partially Overridden)")
        return ""
    }

    function entryTitleFor(entryId, subjectId, title) {
        const source = entryForId(entryId)
        return title || subjectId && AppCentral.scheduleEditor.subjectNameById(subjectId)
            || source && (source.title || source.subjectId && AppCentral.scheduleEditor.subjectNameById(source.subjectId))
            || qsTr("Unnamed Course")
    }

    function timeLabelFor(entryId, startTime, endTime) {
        const source = entryForId(entryId)
        const start = startTime || source && source.startTime || "--:--"
        const end = endTime || source && source.endTime || "--:--"
        return start + " - " + end
    }

    function periodLabelFor(startPeriod, endPeriod) {
        return startPeriod === endPeriod
            ? qsTr("Period %1").arg(startPeriod)
            : qsTr("Periods %1-%2").arg(startPeriod).arg(endPeriod)
    }

    function summaryFor(entryId, weeks, startPeriod, endPeriod, startTime, endTime) {
        return weeksLabel(weeks) + " | " + periodLabelFor(startPeriod, endPeriod)
            + " (" + timeLabelFor(entryId, startTime, endTime) + ")"
    }

    // ── Model lifecycle ────────────────────────────────────────────────
    function reloadOverrides() {
        overrideModel.clear()
        refreshContext()

        const selectedEntryId = entry ? (entry.id || "") : ""
        let selectedIndex = -1
        for (let i = 0; i < baseDayEntries.length; ++i) {
            if (baseDayEntries[i].id === selectedEntryId) {
                selectedIndex = i
                break
            }
        }
        if (selectedIndex < 0)
            return

        const dayOfWeek = selectedDayOfWeek()[0]
        const recordsByIndex = []
        for (let i = 0; i < baseDayEntries.length; ++i)
            recordsByIndex.push(overridesForEntryOnDay(baseDayEntries[i].id, dayOfWeek))

        const signatures = []
        for (const item of recordsByIndex[selectedIndex]) {
            const key = overrideGroupKey(item)
            if (signatures.indexOf(key) === -1)
                signatures.push(key)
        }

        for (const key of signatures) {
            let start = selectedIndex
            let end = selectedIndex
            while (start > 0 && recordWithSignature(recordsByIndex[start - 1], key))
                --start
            while (end + 1 < recordsByIndex.length
                    && recordWithSignature(recordsByIndex[end + 1], key))
                ++end

            const records = []
            for (let i = start; i <= end; ++i)
                records.push(recordWithSignature(recordsByIndex[i], key))
            appendOverrideGroup({ key: key, start: start, end: end, records: records })
        }
    }

    function addDraft() {
        if (!entry || !entry.id)
            return

        refreshContext()
        const source = entry
        const period = basePeriodForId(entry.id)
        const entryIds = [entry.id]
        const dayOfWeek = selectedDayOfWeek()[0]
        const defaultWeeks = defaultWeeksForNewItem(JSON.stringify(entryIds), dayOfWeek)

        collapseAllOverrides()
        overrideModel.append({
            id: "",
            entryId: entry.id,
            entryIds: JSON.stringify(entryIds),
            originalEntryIds: "[]",
            overrideIds: "[]",
            dayOfWeek: encodeDays(selectedDayOfWeek()),
            weeks: encodeWeeks(defaultWeeks),
            subjectId: source.subjectId || "",
            title: source.title || "",
            startTime: source.startTime || "",
            endTime: source.endTime || "",
            originalDayOfWeek: encodeDays(selectedDayOfWeek()),
            originalWeeks: encodeWeeks(defaultWeeks),
            startPeriod: period,
            endPeriod: period,
            isDraft: true,
            removed: false,
            expanded: true
        })

        Qt.callLater(function() {
            overrideFlick.contentY = Math.max(0, overrideFlick.contentHeight - overrideFlick.height)
        })
    }

    // ── Persistence ───────────────────────────────────────────────────
    function saveModelItem(index) {
        // startTime/endTime above are display-only range metadata. Override
        // persistence intentionally stores only subject/title/week/day.
        const item = overrideModel.get(index)
        if (!item || item.removed)
            return

        const targetEntryIds = itemEntryIds(item)
        const originalEntryIds = itemOriginalEntryIds(item)
        const overrideIds = itemOverrideIds(item)
        if (targetEntryIds.length === 0)
            return

        const daysValue = decodeDays(item.dayOfWeek)
        const weeksValue = decodeWeeks(item.weeks)
        const scheduleChanged = !sameValue(item.dayOfWeek, item.originalDayOfWeek)
            || !sameValue(item.weeks, item.originalWeeks)
        const overrideByEntry = ({})
        for (let i = 0; i < originalEntryIds.length; ++i)
            overrideByEntry[originalEntryIds[i]] = overrideIds[i] || ""

        if (scheduleChanged) {
            for (const overrideId of overrideIds) {
                if (overrideId)
                    AppCentral.scheduleEditor.removeOverride(overrideId)
            }
        } else {
            for (const originalEntryId of originalEntryIds) {
                if (targetEntryIds.indexOf(originalEntryId) !== -1)
                    continue
                const overrideId = overrideByEntry[originalEntryId]
                if (overrideId)
                    AppCentral.scheduleEditor.removeOverride(overrideId)
            }
        }

        for (let i = 0; i < targetEntryIds.length; ++i) {
            const targetEntryId = targetEntryIds[i]
            let existingId = scheduleChanged ? "" : (overrideByEntry[targetEntryId] || "")
            if (!existingId)
                existingId = AppCentral.scheduleEditor.findOverride(
                    targetEntryId, daysValue, weeksValue
                ) || ""

            if (existingId) {
                AppCentral.scheduleEditor.updateOverride(
                    existingId, item.subjectId, item.title
                )
            } else {
                AppCentral.scheduleEditor.addOverride(
                    targetEntryId, daysValue, weeksValue, item.subjectId,
                    item.title
                )
            }
        }
    }

    function saveAll() {
        syncing = true

        for (let i = 0; i < overrideModel.count; ++i) {
            const item = overrideModel.get(i)
            if (item && item.removed && !item.isDraft) {
                for (const overrideId of itemOverrideIds(item)) {
                    if (overrideId)
                        AppCentral.scheduleEditor.removeOverride(overrideId)
                }
            }
        }
        for (let i = 0; i < overrideModel.count; ++i)
            saveModelItem(i)

        syncing = false
        reloadOverrides()
        close()
    }

    function clearItem(index) {
        if (index < 0 || index >= overrideModel.count)
            return
        const item = overrideModel.get(index)
        if (item.isDraft) {
            overrideModel.remove(index)
        } else {
            overrideModel.setProperty(index, "removed", true)
            overrideModel.setProperty(index, "expanded", false)
        }
    }

    // ── UI ─────────────────────────────────────────────────────────────
    ColumnLayout {
        id: contentColumn
        Layout.fillWidth: true
        spacing: 4

        Flickable {
            id: overrideFlick
            implicitWidth: 0
            Layout.fillWidth: true
            Layout.preferredHeight: Math.min(contentHeight, root.maxListHeight)
            implicitHeight: Math.min(contentHeight, root.maxListHeight)
            contentWidth: width
            contentHeight: overrideColumn.implicitHeight
            clip: true
            boundsBehavior: Flickable.StopAtBounds

            ScrollBar.vertical: ScrollBar { }

            Column {
                id: overrideColumn
                width: overrideFlick.width
                spacing: 4

                Repeater {
                    model: overrideModel

                    delegate: ScheduleOverrideItem {
                        weeksValue: decodeWeeks(weeks)

                        displayTitle: entryTitleFor(entryId, subjectId, title)
                            + overrideStatusSuffix(
                                overrideIds, weeks, root.selectedDayOfWeek()[0]
                            )
                        summaryText: summaryFor(
                            entryId, weeks, startPeriod, endPeriod, startTime, endTime
                        )
                        everyWeekEnabled: root.everyWeekOptionEnabled(
                            entryIds, root.selectedDayOfWeek()[0], overrideIds
                        )
                        cycleValues: root.cycleValuesForItem(
                            entryIds, root.selectedDayOfWeek()[0], overrideIds
                        )
                        cycleOptions: root.cycleOptionsForValues(cycleValues)
                        blockedWeeks: root.blockedCustomWeeks(
                            entryIds, root.selectedDayOfWeek()[0], overrideIds
                        )
                        startPeriodOptions: root.startPeriodOptionsForItem(
                            startPeriod, endPeriod, entryIds, originalEntryIds
                        )
                        endPeriodOptions: root.endPeriodOptionsForItem(
                            startPeriod, endPeriod, entryIds, originalEntryIds
                        )

                        onToggleRequested: toggleOverride(index)
                        onFieldEdited: (role, value) => overrideModel.setProperty(index, role, value)
                        onWeeksEdited: value => overrideModel.setProperty(
                            index, "weeks", encodeWeeks(value)
                        )

                        onPeriodSelected: (role, period) => applyPeriodSelection(
                            index, role, period
                        )
                        onClearRequested: clearItem(index)
                    }
                }
            }
        }

        Button {
            Layout.fillWidth: true
            Layout.preferredHeight: 34
            flat: true
            enabled: root.entry !== null && !!root.entry.id
            leftPadding: 11
            rightPadding: 11
            topPadding: 4
            bottomPadding: 6
            onClicked: addDraft()

            contentItem: RowLayout {
                spacing: 8
                Icon {
                    name: "ic_fluent_add_20_regular"
                    size: 16
                }
                Text {
                    text: qsTr("New Course")
                    typography: Typography.Body
                }
                Item { Layout.fillWidth: true }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.topMargin: 18
            spacing: 8

            Button {
                Layout.fillWidth: true
                Layout.preferredHeight: 32
                highlighted: true
                text: qsTr("OK")
                onClicked: saveAll()
            }
            Button {
                Layout.fillWidth: true
                Layout.preferredHeight: 32
                text: qsTr("Cancel")
                onClicked: {
                    reloadOverrides()
                    root.close()
                }
            }
        }
    }
}
