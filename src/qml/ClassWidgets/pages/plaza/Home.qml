import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI
import ClassWidgets.Components

FluentPage {
    id: root
    // title: qsTr("Plugin Plaza")
    horizontalPadding: 0
    wrapperWidth: width - 42 * 2

    property var plugins: PlazaBridge.plugins || []
    property var banners: PlazaBridge.banners || []
    property bool loadingPlugins: PlazaBridge.status === "FetchingPlugins" && plugins.length === 0
    property bool loadingBanners: PlazaBridge.status === "FetchingBanners" && banners.length === 0
    property bool loading: loadingPlugins || loadingBanners

    function tagId(tag) {
        if (!tag)
            return ""
        if (typeof tag === "string")
            return tag
        return tag.id || tag.name || ""
    }

    function tagName(tag) {
        if (!tag)
            return ""
        if (typeof tag === "string")
            return tag
        return tag.name || tag.id || ""
    }

    function hasTag(plugin, tag) {
        var tags = plugin && plugin.tags instanceof Array ? plugin.tags : []
        for (var i = 0; i < tags.length; i++) {
            if (tagId(tags[i]) === tag || tagName(tags[i]) === tag)
                return true
        }
        return false
    }

    function pluginSlice(start, count) {
        if (!plugins || plugins.length <= start)
            return []
        return plugins.slice(start, start + count)
    }

    function pluginsByTag(tag, count) {
        if (!plugins || plugins.length === 0)
            return []

        var result = []
        for (var i = 0; i < plugins.length; i++) {
            var plugin = plugins[i]
            if (hasTag(plugin, tag))
                result.push(plugin)
            if (result.length >= count)
                break
        }
        return result
    }

    contentHeader: Item {
        width: parent.width
        height: Math.max(260, Math.min(380, root.width * 0.32))

        BannerCarousel {
            anchors.fill: parent
            plugins: root.plugins
            banners: root.banners
            loading: root.loading
        }
    }

    ColumnLayout {
        Layout.fillWidth: true
        spacing: 16

        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            Text {
                Layout.fillWidth: true
                text: qsTr("Plugins")
                typography: Typography.Subtitle
            }

            // Button {
            //     flat: true
            //     text: qsTr("Open Web Plaza")
            //     icon.name: "ic_fluent_open_20_regular"
            //     onClicked: Qt.openUrlExternally("https://plaza.cw.rinlit.cn")
            // }
        }

        PluginSection {
            Layout.fillWidth: true
            title: qsTr("Recommended for you")
            plugins: root.pluginSlice(0, 9)
            loading: root.loadingPlugins
            pageSize: 6
        }

        PluginSection {
            id: devtoolsSection
            Layout.fillWidth: true
            visible: devtoolsSection.plugins.length > 0 || root.loadingPlugins
            title: qsTr("Developer tools")
            plugins: root.pluginsByTag("开发者工具", 9)
            loading: root.loadingPlugins
            pageSize: 6
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            Text {
                Layout.fillWidth: true
                text: qsTr("All")
                typography: Typography.BodyLarge
            }
        }

        PluginGrid {
            Layout.fillWidth: true
            plugins: root.pluginSlice(0, 12)
            loading: root.loadingPlugins
        }

        InfoBar {
            Layout.fillWidth: true
            visible: !root.loadingPlugins && root.plugins.length === 0
            severity: Severity.Warning
            title: qsTr("No plugins loaded")
            text: qsTr("Please check your network connection or use the refresh button in the title bar to reload the plaza.")
        }
    }
}
