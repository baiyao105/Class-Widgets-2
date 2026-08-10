import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI
import Qt5Compat.GraphicalEffects
import ClassWidgets.Components


FluentWindow {
    id: plazaWindow
    icon: PathManager.assets("images/icons/cw2_settings.png")
    title: qsTr("Plugin Plaza")
    width: Screen.width * 0.7
    height: Screen.height * 0.8
    minimumWidth: 900

    onClosing: function(event) {
        event.accepted = false
        WindowManager.closePlaza()
    }

    titleBarArea: RowLayout {
        anchors.fill: parent
        // spacing: 24


        // search field
        AutoSuggestBox {
            id: searchField
            Layout.alignment: Qt.AlignHCenter
            Layout.maximumWidth: 600
            Layout.fillWidth: true
            placeholderText: qsTr("Search plugins...")
            suggestions: PlazaBridge.plugins || []
            textRole: "name"

            // 选中建议项或按回车：名称精确匹配则直达插件详情页，否则进入搜索页
            onAccepted: {
                var keyword = searchField.text.trim()
                if (!keyword)
                    return
                var plugins = PlazaBridge.plugins || []
                var matched = null
                for (var i = 0; i < plugins.length; i++) {
                    var p = plugins[i]
                    if (p && p.name && p.name.toLowerCase() === keyword.toLowerCase()) {
                        matched = p
                        break
                    }
                }
                if (matched && matched.id) {
                    navigationView.push(PathManager.qml("pages/plaza/Plugin.qml"), { pluginId: matched.id })
                } else {
                    navigationView.push(PathManager.qml("pages/plaza/Search.qml"), { query: keyword })
                }
            }
        }

        ToolButton {
            flat: true
            Layout.alignment: Qt.AlignRight
            icon.name: "ic_fluent_refresh_20_regular"
            size: 18

            ToolTip {
                text: qsTr("Refresh")
                visible: parent.hovered
            }

            onClicked: {
                PlazaBridge.refreshAll()
            }
        }
    }

    Component.onCompleted: {
        PlazaBridge.refreshAll()
    }

    Connections {
        target: PlazaBridge
        function onErrorOccurred(msg) {
            floatLayer.createInfoBar({
                title: qsTr("Error"),
                text: msg,
                severity: Severity.Error,
                timeout: 5000
            })
        }
    }

    navigationItems: [
        {
            title: qsTr("Home"),
            page: PathManager.qml("pages/plaza/Home.qml"),
            icon: "ic_fluent_home_20_regular",
        },
        {
            title: qsTr("Plugins"),
            page: PathManager.qml("pages/plaza/Plugins.qml"),
            icon: "ic_fluent_apps_list_20_regular",
        },
        {
            title: qsTr("Search"),
            page: PathManager.qml("pages/plaza/Search.qml"),
            icon: "ic_fluent_search_20_regular",
        }
    ]



    Watermark {
        anchors.centerIn: parent
    }
}
