import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI
import Widgets
import Qt5Compat.GraphicalEffects

Widget {
    id: root
    text: qsTr("Upcoming")
    width: Math.max(Math.min(implicitWidth, 275), 200)

    property var entries: AppCentral.scheduleRuntime.nextEntries || []
    property var subjects: AppCentral.scheduleRuntime.subjects || []
    property int entriesLength: entries.length < settings.max_activities ? entries.length : settings.max_activities
    property string title: {
        let result = qsTr("Nothing ahead")
        for (let i = 0; i < entriesLength; i++) {
            let entry = entries[i]
            let entryText = entry.title || subjectNameById(entry.subjectId) || qsTr("Unknown")
            result += entryText + (i === entries.length - 1 ? "" : "  ")
        }
        return result
    }

    function subjectNameById(id) {
        for (let i = 0; i < subjects.length; i++) {
            if (subjects[i].id === id)
                return subjects[i].name
        }
        return qsTr("Unknown")
    }

    MarqueeTitle {
        visible: settings.marquee
        anchors.fill: parent
        text: root.title
    }

    Title {
        visible: !settings.marquee
        anchors.centerIn: parent
        text: root.title
    }
}