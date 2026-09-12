import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI
import ClassWidgets.Components

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

    property var weeksValue: "all"

    property string displayTitle: ""
    property string summaryText: ""
    property var cycleOptions: []
    property var cycleValues: []
    property bool everyWeekEnabled: true
    property var blockedWeeks: []
    property var startPeriodOptions: []
    property var endPeriodOptions: []
    required property int startPeriod
    required property int endPeriod

    signal toggleRequested()
    signal fieldEdited(string role, var value)
    signal weeksEdited(var value)

    signal periodSelected(string role, int period)
    signal clearRequested()


    readonly property string repeatType: weeksValue === "all"
        ? "all"
        : (Array.isArray(weeksValue) ? "custom" : "round")
    readonly property int repeatValue: Array.isArray(weeksValue)
        ? Number(weeksValue[0] || 1)
        : (typeof weeksValue === "number" ? weeksValue : 1)

    width: parent ? parent.width : 0
    implicitHeight: removed ? 0 : card.implicitHeight
    height: implicitHeight
    visible: !removed

    function customWeeksText(weeksValue) {
        return Array.isArray(weeksValue)
            ? weeksValue.join("、")
            : String(Math.max(1, Number(weeksValue) || 1))
    }

    function editCustomWeeks(text) {
        const result = []
        const parts = String(text).split(/[,\s，、]+/)
        for (const part of parts) {
            const value = Number(part)
            if (!isFinite(value) || value < 1
                    || result.indexOf(value) !== -1
                    || root.blockedWeeks.indexOf(value) !== -1)
                continue
            result.push(value)
        }
        if (result.length > 0)
            weeksEdited(result)
    }

    function firstAvailableCustomWeek() {
        let value = 1
        while (root.blockedWeeks.indexOf(value) !== -1)
            ++value
        return value
    }

    Frame {
        id: card
        width: parent.width
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
                            text: root.displayTitle
                            typography: Typography.BodyStrong
                            wrapMode: Text.WordWrap
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
                            text: qsTr("One Specific Week")
                            ButtonGroup.group: repeatGroup
                            checked: root.repeatType === "custom"
                            onClicked: root.weeksEdited([root.firstAvailableCustomWeek()])
                        }
                    }

                    RowLayout {
                        visible: root.repeatType === "round"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 32
                        spacing: 10
                        Text { text: qsTr("Week") }
                        ComboBox {
                            Layout.fillWidth: true
                            model: root.cycleOptions
                            currentIndex: root.cycleValues.indexOf(root.repeatValue)
                            onActivated: {
                                if (currentIndex >= 0)
                                    root.weeksEdited(root.cycleValues[currentIndex])
                            }
                        }
                        Text { text: qsTr("of every %1 weeks").arg(root.cycleOptions.length) }
                    }

                    RowLayout {
                        visible: root.repeatType === "custom"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 32
                        spacing: 10
                        Text { text: qsTr("Weeks") }
                        TextField {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 32
                            text: root.customWeeksText(root.weeksValue)
                            placeholderText: qsTr("e.g. 2, 4, 6")
                            onTextEdited: root.editCustomWeeks(text)
                        }
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
                        spacing: 10
                        Text { text: qsTr("Period") }
                        ComboBox {
                            Layout.fillWidth: true
                            Layout.minimumWidth: 42
                            model: root.startPeriodOptions
                            currentIndex: root.startPeriodOptions.indexOf(root.startPeriod)
                            onActivated: {
                                if (currentIndex >= 0)
                                    root.periodSelected("startTime", Number(model[currentIndex]))
                            }
                        }
                        Text { text: qsTr("to") }
                        ComboBox {
                            Layout.fillWidth: true
                            Layout.minimumWidth: 42
                            model: root.endPeriodOptions
                            currentIndex: root.endPeriodOptions.indexOf(root.endPeriod)
                            onActivated: {
                                if (currentIndex >= 0)
                                    root.periodSelected("endTime", Number(model[currentIndex]))
                            }
                        }
                    }
                }

            }
        }
    }
}
