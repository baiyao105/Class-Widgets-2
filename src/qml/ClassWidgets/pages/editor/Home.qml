import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI
import ClassWidgets.Components

import QtQuick.Effects  // shadow

FluentPage {
    title: qsTr("Home")

    property string _pendingScheduleName: ""

    Introduction {
        source:PathManager.images(
            "editor/new_editor_schedule-" + (Theme.isDark()? "dark" : "light") + ".png"
        )
        title: qsTr("The new way to edit schedules")
        description: qsTr(
            "1. Tap and drag to adjust class times;\n" +
            "2. Quickly fill in courses at a glance;\n" +
            "3. Done in just 3 steps — editing your schedule has never been easier!"
        )
        RowLayout {
            Layout.alignment: Qt.AlignRight

            Button {
                flat: true
                Layout.alignment: Qt.AlignRight
                icon.name: "ic_fluent_folder_open_20_regular"
                text: qsTr("Open schedules folder")
                onClicked: AppCentral.scheduleManager.openSchedulesFolder()
            }

            ToolSeparator {
                Layout.fillHeight: true
            }
            Button {
                enabled: !AppCentral.scheduleManager.isReadonly()
                flat: true
                highlighted: true
                icon.name: "ic_fluent_add_20_regular"
                text: qsTr("New Schedule")
                onClicked: scheduleSetupDialog.open()
            }
        }
    }

    ColumnLayout {
        Layout.fillWidth: true
        Text {
            typography: Typography.BodyStrong
            text: qsTr("Your schedules")
            Layout.fillWidth: true
        }

        Grid {
            Layout.fillWidth: true
            columns: Math.floor(width / (278 + rowSpacing / 2)) // 自动算列数
            rowSpacing: 8
            columnSpacing: 8

            Repeater {
                model: AppCentral.scheduleManager.schedules()
                delegate: ScheduleClip {
                    filename: modelData.name
                    selected: AppCentral.scheduleManager.currentScheduleName === modelData.name
                    onClicked: {
                        if (AppCentral.scheduleEditor.dirty) {
                            _pendingScheduleName = modelData.name
                            switchScheduleDialog.open()
                        } else {
                            AppCentral.scheduleManager.load(modelData.name)
                        }
                    }
                }
            }
        }
    }


    Dialog {
        id: switchScheduleDialog
        modal: true
        title: qsTr("Save changes to the timetable")
        Text {
            Layout.fillWidth: true
            text: qsTr("Do you want to save the changes to \"%1\"?").arg(AppCentral.scheduleEditor.filename)
        }
        standardButtons: Dialog.Save | Dialog.Discard | Dialog.Cancel

        onAccepted: {
            let result = AppCentral.scheduleManager.save()
            if (result) {
                AppCentral.scheduleEditor.markSaved()
                AppCentral.scheduleManager.load(_pendingScheduleName)
            } else {
                floatLayer.createInfoBar({
                    title: qsTr("Save Failed"),
                    severity: Severity.Error,
                    text: qsTr("Failed to save schedule, see log for details")
                })
            }
        }
        onDiscarded: {
            AppCentral.scheduleEditor.markSaved()
            AppCentral.scheduleManager.load(_pendingScheduleName)
        }
        onRejected: {
            close()
        }
    }

    ScheduleSetupDialog {
        id: scheduleSetupDialog

        onScheduleCreated: {
            floatLayer.createInfoBar({
                severity: Severity.Success,
                title: qsTr("Schedule Created"),
                text: qsTr("The schedule has been created successfully.")
            })
        }
    }
}
