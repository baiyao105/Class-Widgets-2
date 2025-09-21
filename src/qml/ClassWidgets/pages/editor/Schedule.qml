import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI
import ClassWidgets.Components

import QtQuick.Effects  // shadow

Item {
    FileHud { id: fileHud }

    RowLayout {
        id: rowLayout
        anchors.fill: parent
        anchors.margins: 24
        anchors.topMargin: 24 + fileHud.height
        spacing: 10

        ScheduleTableView {
            id: scheduleTable
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentWeek: weekSelector.currentWeek

            onCellClicked: (row, column, entry, delegate) => {
                entryFlyout.entry = entry
                entryFlyout.selectedCell = selectedCell
                entryFlyout.weekSelector = weekSelector
                entryFlyout.parent = delegate   // 定位到点击的 cell
                entryFlyout.open()
            }
        }

        ScheduleFlyout {
            id: entryFlyout
        }

        ColumnLayout {
            Layout.maximumWidth: 275
            spacing: 12
            SettingExpander {
                Layout.fillWidth: true
                // Layout.fillHeight: true
                expanded: true
                title: qsTr("Week Cycle")
                icon.name: "ic_fluent_calendar_week_numbers_20_regular"

                WeekSelector {
                    Layout.margins: 18
                    id: weekSelector    
                    onCurrentWeekChanged: {
                        scheduleTable.currentWeek = currentWeek
                    }
                }
            }

            // 快速添加学科
            Frame {
                Layout.fillWidth: true
                Layout.fillHeight: true
                padding: 16

                ColumnLayout {
                    anchors.fill: parent
                    spacing: 8
                    Text {
                        typography: Typography.BodyStrong
                        text: qsTr("Quick Add Subject")
                    }

                    Flow {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Repeater {
                            model: AppCentral.scheduleRuntime.subjects
                            Button {
                                flat: true
                                icon.name: modelData.icon
                                text: modelData.name
                                onClicked: {
                                    quickAddSubject(modelData.id)
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    function quickAddSubject(subjectid) {
        let row = scheduleTable.selectedCell.row
        let column = scheduleTable.selectedCell.column

        // 如果没有选中单元格，默认选择第一行第一列
        if (row < 0 || column < 0) {
            row = 0
            column = 0
        }

        let day = scheduleTable.getDayByColumn(column)
        let entry = scheduleTable.getEntryByDayAndRow(day, row, column)
        if (!entry) return;

        let weeks;
        if (scheduleTable.currentWeek === -1) {
            weeks = "all"; // 字符串
        } else if (Array.isArray(scheduleTable.currentWeek)) {
            weeks = scheduleTable.currentWeek.map(w => Number(w)); // 强制 int
        } else {
            weeks = Number(scheduleTable.currentWeek); // 单 int
        }

        let dayOfWeek = [column + 1]

        // 调用 scheduleEditor 的逻辑
        const existingId = AppCentral.scheduleEditor.findOverride(entry.id, dayOfWeek, weeks)
        if (existingId) {
            AppCentral.scheduleEditor.updateOverride(existingId, subjectid, null)
        } else {
            AppCentral.scheduleEditor.addOverride(entry.id, dayOfWeek, weeks, subjectid, null)
        }

        // 更新表格显示
        scheduleTable.currentEntry = scheduleTable.getEntryByDayAndRow(day, row, column)

        // 移动焦点到下一行
        let nextRow = row + 1
        let nextColumn = column

        if (nextRow === scheduleTable.maxRows) {
            nextRow = 0
            nextColumn = column + 1
            if (nextColumn >= 7) nextColumn = 0 // 超出一周列就回到第一列
        }

        scheduleTable.selectedCell = { row: nextRow, column: nextColumn }
    }
}