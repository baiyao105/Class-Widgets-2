import QtQuick
import RinUI


// 小组件加载器 -> model: WidgetsModel
Loader {
    id: loader
    source: model.qmlPath
    asynchronous: true
    anchors.centerIn: parent
    onStatusChanged: {
        if (status === Loader.Ready) {
            if (item && model.backendObj) {
                item.backend = model.backendObj
            }
            if (item && model.settings) {
                item.settings = model.settings
            }
            anim.start()
        }
    }

    Connections {
        target: WidgetsModel
        function onModelChanged() {
            if (loader.item && model.settings) {
                loader.item.settings = model.settings
            }
        }
    }
}