import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI

Button {
    id: delegate
    flat: true
    highlighted: checked

    property var subjects: AppCentral.scheduleRuntime.subjects || []

    property var day: {}
    property var entry: {}
    text: entry ? entry.title || AppCentral.scheduleEditor.subjectNameById(entry.subjectId) || qsTr("Unset") : undefined
    opacity: entry ? (entry.title || AppCentral.scheduleEditor.subjectNameById(entry.subjectId)) ? 1 : 0.5 : 1
    enabled: entry
}
