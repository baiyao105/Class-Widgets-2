import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window as QQW
import Widgets

QQW.Window {
    id: root
    visible: true
    flags: Qt.FramelessWindowHint | Qt.Window
    // width: Screen.width
    // height: Screen.height
    width: 1200
    height: 200
    color: "transparent"

    Row {
        id: widgetContainer
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 10
        Widget {
            text: "测试组件"
            Title {
                text: Qt.formatDateTime(new Date(), "yyyy-MM-dd hh:mm:ss")
            }
        }
    }
}
