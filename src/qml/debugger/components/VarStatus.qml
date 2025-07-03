import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI


GridLayout {
    id: varStatusLayout
    property alias model: varStatusRepeater.model
    columns: 2
    rowSpacing: 12
    columnSpacing: 24

    Repeater {
        id: varStatusRepeater
        model: [
            {"name": "current_time", "value": "null", tips: "当前时间"}
        ]

        delegate: RowLayout {
            Layout.fillWidth: true
            // left
            Text {
                color: Colors.proxy.textSecondaryColor
                text: modelData.name + ":"
                Layout.fillWidth: true

                HoverHandler {
                    id: hoverHandler
                    enabled: modelData.hasOwnProperty("tips")
                }

                ToolTip {
                    id: toolTip
                    text: modelData.hasOwnProperty("tips") ? modelData.tips : ""
                    visible: hoverHandler.hovered
                }
            }
            // right value
            Text {
                horizontalAlignment: Text.AlignRight
                Layout.fillWidth: true
                text: modelData.value
                // 换行
                wrapMode: Text.Wrap
            }
        }
    }
}