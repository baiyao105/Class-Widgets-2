import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI

Window {
    id: presetEditor
    width: 400
    height: 500
    title: "Presets Editor 调试预设编辑器"

    property string selectedPreset: WidgetModel.currentPreset

    // 载入当前预设启用组件列表到文本框
    function loadEnabledWidgets() {
        var list = WidgetModel.presets[selectedPreset] || []
        console.log("233"+list)
        enabledWidgetsArea.text = list.join(",")
    }

    Column {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

        // 预设选择
        ComboBox {
            id: presetCombo
            model: Object.keys(WidgetModel.presets)  // 直接访问后端_presets属性，调试用，正式建议封装接口
            currentIndex: model.indexOf(selectedPreset)

            onCurrentIndexChanged: {
                selectedPreset = model[currentIndex]
                WidgetModel.switchPreset(selectedPreset)
                loadEnabledWidgets()
            }
        }

        // 显示和编辑当前启用组件ID（逗号分隔的字符串）
        TextArea {
            id: enabledWidgetsArea
            placeholderText: "启用组件ID，逗号分隔"
            wrapMode: TextArea.Wrap
            font.pixelSize: 16
            height: 200
            text: WidgetModel.enabledWidgets.join(",")
        }

        Button {
            text: "保存并应用预设"
            onClicked: {
                var ids = enabledWidgetsArea.text.split(",").map(function(s) { return s.trim() }).filter(function(s){ return s.length > 0 })
                WidgetModel.updatePreset(selectedPreset, ids)
                WidgetModel.switchPreset(selectedPreset)
            }
        }

        Component.onCompleted: loadEnabledWidgets()
    }
}