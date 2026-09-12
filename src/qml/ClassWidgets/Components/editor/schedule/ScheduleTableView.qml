import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt.labs.qmlmodels
import RinUI
import ClassWidgets.Components

Item {
    id: root
    clip: true

    property int itemWidth: Math.max(root.width / 7, 120)

    // 当前显示的绝对周次（从开学日期计算）
    property int currentWeek: 1

    // 当前周的起始日期（周日）
    readonly property var weekStart: weekStartFor(currentWeek)

    // 暴露当前选中状态
    property alias selectedCell: table.selectedCell
    property alias currentEntry: table.currentEntry
    property alias maxRows: table.maxRows

    // 发出信号
    signal cellClicked(int row, int column, var entry, Item delegate)

    // ── 日期 / 星期工具 ────────────────────────────────

    function parseDate(str) {
        var p = String(str).split("-");
        return new Date(Number(p[0]), Number(p[1]) - 1, Number(p[2]));
    }

    // 第 week 周（绝对周次）的起始日期，回退到本周的周日
    function weekStartFor(week) {
        var start = parseDate(AppCentral.scheduleEditor.meta.startDate);
        if (!isFinite(start.getTime()))
            start = new Date(); // 无开学日期时回退到本周
        var block = new Date(start.getTime() + (week - 1) * 7 * 86400000);
        block.setDate(block.getDate() - block.getDay()); // getDay(): 0=周日
        return block;
    }

    // 第 column 列的日期
    function columnDate(columnIndex) {
        return new Date(weekStart.getTime() + columnIndex * 86400000);
    }

    // 第 column 列对应的星期几（1=周一 ... 7=周日）。列序：周日、周一 … 周六
    function dayOfWeekForColumn(columnIndex) {
        return (columnIndex + 6) % 7 + 1;
    }

    // 绝对周次 → 周期内周次
    function cycleWeekFor(week) {
        var cycle = Math.max(1, AppCentral.scheduleEditor.meta.maxWeekCycle);
        if (week >= 1) return ((week - 1) % cycle) + 1;
        return (((week % cycle) + cycle) % cycle) + 1;
    }

    function isToday(date) {
        var now = new Date();
        return date.getFullYear() === now.getFullYear()
            && date.getMonth() === now.getMonth()
            && date.getDate() === now.getDate();
    }

    // 根据列号找到 day
    function getDayByColumn(columnIndex) {
        var weekday = dayOfWeekForColumn(columnIndex);
        var days = AppCentral.scheduleEditor.entriesData;

        for (let i = 0; i < days.length; i++) {
            var day = days[i];
            if (day.date) continue; // 跳过指定日期

            let validDay = !day.dayOfWeek || day.dayOfWeek.indexOf(weekday) !== -1;
            let validWeek = isWeekActive(day.weeks);

            if (validDay && validWeek) return day;
        }
        return null;
    }

    function isWeekActive(weeks) {
        if (!weeks || weeks === "all") return true;

        let maxWeekCycle = AppCentral.scheduleEditor.meta.maxWeekCycle;

        if (Array.isArray(weeks)) {
            return weeks.indexOf(table.currentWeek) !== -1;
        }
        if (typeof weeks === "number") {
            return table.currentWeek >= weeks && (table.currentWeek - weeks) % maxWeekCycle === 0;
        }

        return false;
    }

    // 根据 row / column 从批量快照中取已应用 override 的 entry。
    function getEntryByDayAndRow(day, row, columnIndex) {
        const columns = table.effectiveEntries;
        if (!columns || columnIndex < 0 || columnIndex >= columns.length)
            return null;
        const entries = columns[columnIndex];
        return entries && row >= 0 && row < entries.length ? entries[row] : null;
    }

    // 表头（日历样式：日期 + 星期，横排）
    ScheduleHeader {
        id: headerRow
        weekStart: root.weekStart
        itemWidth: root.itemWidth
        contentX: table.contentX
    }

    TableView {
        id: table
        anchors.top: headerRow.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom

        rowSpacing: 0
        columnSpacing: 0

        property var currentWeek: root.currentWeek
        property var selectedCell: ({ row: -1, column: -1 })
        property var currentEntry: null
        property int entriesRevision: AppCentral.scheduleEditor.entriesRevision
        property int overridesRevision: AppCentral.scheduleEditor.overridesRevision
        property var effectiveEntries: {
            // Explicit dependencies keep the one batch query in sync with edits.
            const entriesRevisionValue = entriesRevision
            const overridesRevisionValue = overridesRevision
            return AppCentral.scheduleEditor.getEffectiveEntries(currentWeek)
        }

        // 动态计算行数（最大 class 数量）
        property int maxRows: {
            var maxLen = 0;
            const columns = effectiveEntries || [];
            for (var col = 0; col < columns.length; col++) {
                if (columns[col].length > maxLen)
                    maxLen = columns[col].length;
            }
            return maxLen;
        }

        model: maxRows

        delegate: Item {
            property bool isEvenRow: row % 2 === 0
            implicitWidth: entriesLayout.childrenRect.width
            implicitHeight: entriesLayout.childrenRect.height

            Rectangle {
                anchors.fill: parent
                color: Colors.proxy.subtleSecondaryColor
                radius: 6
                visible: isEvenRow
            }

            Row {
                id: entriesLayout
                spacing: 0
                Repeater {
                    model: 7
                    delegate: TableEntryDelegate {
                        id: entryDelegate
                        width: itemWidth
                        height: 60

                        checkable: true
                        checked: (table.selectedCell.row === row && table.selectedCell.column === index)

                        entry: root.getEntryByDayAndRow(null, row, index)

                        onClicked: {
                            table.selectedCell = { row: row, column: index }
                            table.currentEntry = entry
                            root.cellClicked(row, index, entry, entryDelegate)
                        }
                    }
                }
            }
        }
    }
}
