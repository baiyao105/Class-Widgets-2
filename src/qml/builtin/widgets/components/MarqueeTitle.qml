import QtQuick
import QtQuick.Controls
import RinUI
import Widgets

Item {
    id: marquee
    width: 200
    height: label.height
    clip: true

    property alias text: label.text
    property alias font: label.font
    property int speed: 50
    property bool running: true

    Title {
        id: label
        // text: "滚木字幕滚木字幕滚木字幕滚木字幕滚木字幕滚木字幕"
        anchors.verticalCenter: parent.verticalCenter

        NumberAnimation on x {
            id: scrollAnim
            loops: Animation.Infinite
            from: marquee.width
            to: -label.width
            duration: (label.width + marquee.width) * 1000 / Math.max(1, marquee.speed)
            running: false
        }
    }

    // 初次与参数变化时，重启动画
    Component.onCompleted: restart()
    onRunningChanged: restart()
    onSpeedChanged: restart()
    Connections {
        target: label
        function onWidthChanged() { restart(); }
        function onTextChanged()  { restart(); }
    }

    function restart() {
        scrollAnim.stop()
        if (!running) return

        if (label.implicitWidth <= marquee.width) {
            label.x = (marquee.width - label.width) / 2
            return
        }
        // 重新计算并开滚
        scrollAnim.from = marquee.width
        scrollAnim.to   = -label.width
        scrollAnim.duration = (label.width + marquee.width) * 1000 / Math.max(1, marquee.speed)
        label.x = marquee.width
        scrollAnim.start()
    }
}
