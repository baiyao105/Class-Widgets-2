import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI


Text {
    id: title
    readonly property bool miniMode: Configs.data.preferences.mini_mode
    property int px: miniMode? 22 : 28

    font.bold: true
    font.pixelSize: px

    Behavior on px { NumberAnimation { duration: 400; easing.type: Easing.OutQuint } }
}