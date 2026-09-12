import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI
import ClassWidgets.Components

import QtQuick.Effects  // shadow

Item {
    id: root

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

        // 新设计下 currentWeek 恒为绝对周次，写入 override 时统一换算成周期内周次
        let weeks = scheduleTable.cycleWeekFor(root.currentWeek);
        let dayOfWeek = [scheduleTable.dayOfWeekForColumn(column)]

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

    property bool editable: !AppCentral.scheduleManager.isReadonly()  // 是否可编辑

    // 当前显示的绝对周次，默认直接跳转到本周（周数由开学日期计算得出）
    property int currentWeek: Math.max(1, AppCentral.scheduleRuntime.currentWeek || 1)

    // 供 ScheduleFlyout 读取的周上下文
    QtObject {
        id: weekContext
        property int currentWeek: root.currentWeek
        property int maxWeekCycle: AppCentral.scheduleEditor.meta.maxWeekCycle
    }

    ColumnLayout {
        id: mainLayout
        anchors.fill: parent
        anchors.margins: 24
        spacing: 10

        // 顶部：周标题 + 月份 + 上一周 / 今日 / 下一周
        RowLayout {
            Layout.fillWidth: true

            ColumnLayout {
                spacing: 0
                Layout.alignment: Qt.AlignBottom

                Text {
                    text: qsTr("Week %1").arg(root.currentWeek)
                    typography: Typography.Title
                }
                Text {
                    text: Qt.locale().toString(scheduleTable.weekStart, "yyyy 年 M 月")
                    typography: Typography.Body
                    color: Colors.proxy.textSecondaryColor
                }
            }

            Item {
                Layout.fillWidth: true
            }

            RowLayout {
                Layout.alignment: Qt.AlignBottom
                spacing: 8

                ToolButton {
                    icon.name: "ic_fluent_chevron_left_20_regular"
                    implicitWidth: 32
                    implicitHeight: 32
                    onClicked: root.currentWeek--
                }
                Button {
                    text: qsTr("今日")
                    implicitHeight: 32
                    onClicked: root.currentWeek = Math.max(1, AppCentral.scheduleRuntime.currentWeek || 1)
                }
                ToolButton {
                    icon.name: "ic_fluent_chevron_right_20_regular"
                    implicitWidth: 32
                    implicitHeight: 32
                    onClicked: root.currentWeek++
                }
            }
        }

        ScheduleTableView {
            id: scheduleTable
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentWeek: root.currentWeek

            onCellClicked: (row, column, entry, delegate) => {
                if (!editable) {
                    return
                }
                entryFlyout.entry = entry
                entryFlyout.selectedCell = { row: row, column: column }
                entryFlyout.weekSelector = weekContext
                entryFlyout.parent = delegate   // 定位到点击的 cell
                entryFlyout.open()
            }
        }


        ScheduleFlyout {
            id: entryFlyout
        }
    }


    // 快速添加学科：悬浮于页面右下角（不进布局，位置由组件自管理），Header 可 XY 拖动，松手 Y 吸附回底部
    AddSubjectExpander {
        id: addSubject
        width: 350
        snapDuration: 380
        maxDragUp: 420
        onSubjectClicked: (subjectId) => quickAddSubject(subjectId)
        sourceItem: mainLayout
    }
}
