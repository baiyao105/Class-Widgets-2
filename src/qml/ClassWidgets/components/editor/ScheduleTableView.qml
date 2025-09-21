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

    // 暴露当前选中状态
    property alias currentWeek: table.currentWeek
    property alias selectedCell: table.selectedCell
    property alias currentEntry: table.currentEntry
    property alias maxRows: table.maxRows

    // 发出信号
    signal cellClicked(int row, int column, var entry, Item delegate)

    // 根据列号找到 day
    function getDayByColumn(columnIndex) {
        var weekday = columnIndex + 1;
        var week = table.currentWeek;

        for (var i = 0; i < AppCentral.scheduleEditor.days.length; i++) {
            var day = AppCentral.scheduleEditor.days[i];
            if (day.date) continue; // 跳过指定日期

            var validDay = !day.dayOfWeek || day.dayOfWeek.indexOf(weekday) !== -1;

            var validWeek = false;
            if (!day.weeks || day.weeks === "all") validWeek = true;
            else if (Array.isArray(day.weeks) && day.weeks.indexOf(week) !== -1) validWeek = true;
            else if (typeof day.weeks === "number" && day.weeks === week) validWeek = true;

            if (validDay && validWeek) return day;
        }
        return null;
    }

    // 根据 day 和 row 找 entry，并应用 overrides
    function getEntryByDayAndRow(day, row, columnIndex) {
        if (!day || !day.entries) return null;

        let classEntries = day.entries.filter(e => e.type === "class");
        if (row >= classEntries.length) return null;

        let e = classEntries[row];
        let week = table.currentWeek;
        let weekday = columnIndex + 1;

        return AppCentral.scheduleEditor.getEntryOverride(e.id, week, weekday);
    }

    // 表头
    Row {
        id: headerRow
        height: 40
        x: -table.contentX

        Repeater {
            model: 7
            delegate: Item {
                width: itemWidth
                height: parent.height
                Text {
                    anchors.centerIn: parent
                    text: Qt.locale().dayName((index + 1) % 7, Locale.ShortFormat)
                    color: Colors.proxy.textSecondaryColor
                    font.bold: true
                }
            }
        }
    }

    TableView {
        id: table
        anchors.top: headerRow.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom

        rowSpacing: 0
        columnSpacing: 0

        property int currentWeek: -1 // -1 表示全周
        property var selectedCell: ({ row: -1, column: -1 })
        property var currentEntry: null

        // 动态计算行数（最大 class 数量）
        property int maxRows: {
            var maxLen = 0;
            for (var col = 0; col < 7; col++) {
                var day = root.getDayByColumn(col);
                if (!day || !day.entries) continue;

                let classEntries = day.entries.filter(function(e) { return e.type === "class"; });
                if (classEntries.length > maxLen)
                    maxLen = classEntries.length;
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

                        day: root.getDayByColumn(index)
                        entry: root.getEntryByDayAndRow(day, row, index)

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
