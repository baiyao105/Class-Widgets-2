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
                text: "已加载组件：" + widgetRepeater.count
                Component.onCompleted: {
                    console.log(widgetRepeater.models)
                }
            }
        }
        Repeater {
            id: widgetRepeater
            model: WidgetModel
            delegate: Loader {
                source: qmlPath
                onLoaded: {
                    console.log("onLoaded: " + qmlPath)
                }
            }
        }
    }
}
