import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI
import ClassWidgets.Components

import QtQuick.Effects  // shadow

FluentPage {
    title: qsTr("Home")

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
        Button {
            flat: true
            Layout.alignment: Qt.AlignRight
            icon.name: "ic_fluent_folder_open_20_regular"
            text: qsTr("Open schedules folder")
            onClicked: AppCentral.scheduleManager.openSchedulesFolder()
        }
        Button {
            flat: true
            highlighted: true
            Layout.alignment: Qt.AlignRight
            icon.name: "ic_fluent_add_20_regular"
            text: qsTr("Create a new schedule")
            onClicked: createScheduleDialog.open()
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
                        AppCentral.scheduleManager.load(modelData.name)
                    }
                }
            }
        }
    }


    Dialog {
        id: createScheduleDialog
        modal: true
        title: qsTr("Create a new schedule")
        Text {
            Layout.fillWidth: true
            text: qsTr("Enter a name for your new schedule")
        }

        ColumnLayout {
            Layout.fillWidth: true
            TextField {
                id: scheduleNameField
                Layout.fillWidth: true
                placeholderText: qsTr("Schedule name")
                onTextChanged: {
                    const okBtn = createScheduleDialog.footer.standardButton(DialogButtonBox.Ok)
                    okBtn.enabled = scheduleNameField.text.length > 0 &&
                        !AppCentral.scheduleManager.checkNameExists(scheduleNameField.text)
                    validator.visible = true
                }
            }
            Text {
                id: validator
                visible: false
                Layout.fillWidth: true
                typography: Typography.Caption
                color: {
                    if (!scheduleNameField.text) {
                        return Colors.proxy.systemCriticalColor
                    }
                    if (AppCentral.scheduleManager.checkNameExists(scheduleNameField.text)) {
                        return Colors.proxy.systemCriticalColor
                    }
                    return Colors.proxy.systemSuccessColor
                }
                text: {
                    if (!scheduleNameField.text) {
                        return qsTr("Cannot be empty (⊙x⊙;)")
                    }
                    if (AppCentral.scheduleManager.checkNameExists(scheduleNameField.text)) {
                        return qsTr("Cannot duplicate existing name (⊙x⊙;)")
                    }
                    return qsTr("Great! That's it. ヾ(≧▽≦*)o")
                }
            }
        }

        footer: DialogButtonBox {
            standardButtons: DialogButtonBox.Ok | DialogButtonBox.Cancel

            onAccepted: {
                AppCentral.scheduleManager.add(scheduleNameField.text)
                createScheduleDialog.close()
            }
            onRejected: createScheduleDialog.close()

            Component.onCompleted: {
                const okBtn = standardButton(DialogButtonBox.Ok)
                okBtn.enabled = false // 初始禁用
            }
        }
    }
}