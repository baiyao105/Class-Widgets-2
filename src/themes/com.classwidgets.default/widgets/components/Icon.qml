import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI


Icon {
    id: text
    readonly property bool miniMode: Configs.data.preferences.mini_mode
    size: miniMode? 22 : 28
}