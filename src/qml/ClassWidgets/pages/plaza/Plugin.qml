import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI
import ClassWidgets.Components

FluentPage {
    id: root
    property string pluginId: ""

    title: manifest && manifest.name ? manifest.name : qsTr("Plugin Detail")
    horizontalPadding: 0
    wrapperWidth: width - 42 * 2

    property string baseUrl: "https://plaza.cw.rinlit.cn"
    property var manifest: null
    property string readme: ""
    property string readmeHtml: ""
    property var tagsMap: ({})
    property var otherPlugins: []
    property bool manifestLoading: false
    property bool readmeLoading: false
    property bool tagsLoading: false
    property bool otherPluginsLoading: false
    property string errorMessage: ""
    property string iconSource: pluginId ? resourceUrl(pluginId, "icon") : ""

    Component.onCompleted: loadPlugin()
    onPluginIdChanged: loadPlugin()

    function loadPlugin() {
        if (!pluginId)
            return

        manifest = null
        readme = ""
        readmeHtml = ""
        otherPlugins = []
        errorMessage = ""
        iconSource = resourceUrl(pluginId, "icon")
        fetchManifest()
        fetchTags()
    }

    function apiUrl(path) {
        return baseUrl + path
    }

    function pluginApiUrl(pluginId, suffix) {
        return apiUrl("/api/plugins/" + encodeURIComponent(pluginId) + suffix)
    }

    function resourceUrl(pluginId, resource) {
        return pluginId ? pluginApiUrl(pluginId, "/resources/" + resource) : ""
    }

    function repoUrl() {
        return manifest ? (manifest.repo_url || manifest.url || "") : ""
    }

    function tagId(tag) {
        if (!tag)
            return ""
        if (typeof tag === "string")
            return tag
        return tag.id || tag.name || ""
    }

    function tagDisplayName(tag) {
        if (!tag)
            return ""
        if (typeof tag === "string")
            return tagName(tag)
        return tag.name || tagName(tag.id) || tag.id || ""
    }

    function tagKeyMap(tags) {
        var map = ({})
        if (!(tags instanceof Array))
            return map
        for (var i = 0; i < tags.length; i++) {
            var id = tagId(tags[i])
            var name = tagDisplayName(tags[i])
            if (id)
                map[id] = true
            if (name)
                map[name] = true
        }
        return map
    }

    function requestText(url, success, failure) {
        var xhr = new XMLHttpRequest()
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status >= 200 && xhr.status < 300) {
                    success(xhr.responseText)
                } else if (failure) {
                    failure(xhr.status + " " + xhr.statusText)
                }
            }
        }
        xhr.open("GET", url)
        xhr.send()
    }

    function fetchManifest() {
        manifestLoading = true
        requestText(pluginApiUrl(pluginId, ""), function(text) {
            try {
                var response = JSON.parse(text)
                manifest = response && response.ok && response.data ? response.data : response
                manifestLoading = false
                fetchReadme()
                fetchOtherPlugins()
            } catch (e) {
                manifestLoading = false
                errorMessage = qsTr("Failed to parse plugin information.")
            }
        }, function(error) {
            manifestLoading = false
            errorMessage = qsTr("Failed to load plugin information: ") + error
        })
    }

    function fetchReadme() {
        readmeLoading = true
        requestText(resourceUrl(pluginId, "readme"), function(text) {
            readme = preprocessReadme(text)
            readmeHtml = MarkdownRenderBridge.render(readme)
            readmeLoading = false
        }, function() {
            readme = "# " + qsTr("No description") + "\n" + qsTr("This plugin does not provide README content.")
            readmeHtml = MarkdownRenderBridge.render(readme)
            readmeLoading = false
        })
    }

    function fetchTags() {
        tagsLoading = true
        requestText(baseUrl + "/api/plugins/tags", function(text) {
            try {
                var response = JSON.parse(text)
                var map = ({})
                var tags = response && response.ok && response.data instanceof Array ? response.data : []
                for (var i = 0; i < tags.length; i++) {
                    if (tags[i] && tags[i].id)
                        map[tags[i].id] = tags[i].name || tags[i].id
                }
                tagsMap = map
            } catch (e) {
                tagsMap = ({})
            }
            tagsLoading = false
        }, function() {
            tagsMap = ({})
            tagsLoading = false
        })
    }

    function fetchOtherPlugins() {
        otherPluginsLoading = true
        requestText(baseUrl + "/api/plugins?per_page=50", function(text) {
            try {
                var response = JSON.parse(text)
                var list = response && response.data instanceof Array ? response.data : []
                otherPlugins = pickRelatedPlugins(list)
            } catch (e) {
                otherPlugins = []
            }
            otherPluginsLoading = false
        }, function() {
            otherPlugins = []
            otherPluginsLoading = false
        })
    }

    function pickRelatedPlugins(list) {
        var result = []
        var tags = manifest && manifest.tags instanceof Array ? manifest.tags : []
        var currentTags = tagKeyMap(tags)

        for (var i = 0; i < list.length; i++) {
            var plugin = list[i]
            if (!plugin || plugin.id === pluginId)
                continue

            var pluginTags = plugin.tags instanceof Array ? plugin.tags : []
            var matched = tags.length === 0
            for (var j = 0; j < pluginTags.length && !matched; j++) {
                var id = tagId(pluginTags[j])
                var name = tagDisplayName(pluginTags[j])
                matched = (id && currentTags[id]) || (name && currentTags[name])
            }

            if (matched)
                result.push(plugin)

            if (result.length >= 6)
                break
        }
        return result
    }

    function preprocessReadme(text) {
        var result = text || ""
        result = result.replace(/\$\{__web_page_repo__\}/g, repoUrl())
        result = result.replace(/\$\{__web_page_stars_badge__\}/g, "")
        result = result.replace(/\$\{__web_page_downloads_badge__\}/g, "")
        result = result.replace(/\$\{__web_page_license_badge__\}/g, "")
        result = result.replace(/\$\{__web_page_link:(https?:\/\/[^}]+)__\}/g, "$1")
        result = result.replace(/\$\{__web_page_badge:(https?:\/\/[^}]+)__\}/g, "")
        return result
    }

    function tagName(id) {
        if (!id)
            return ""
        var tag = tagsMap ? tagsMap[id] : null
        return tag || id
    }

    function releasePageUrl() {
        return pluginId ? resourceUrl(pluginId, "release?format=cwplugin") : ""
    }

    function openPlugin(plugin) {
        if (!plugin || !plugin.id)
            return
        navigationView.push(Qt.resolvedUrl("Plugin.qml"), { pluginId: plugin.id })
    }

    function openUrl(url) {
        if (url)
            Qt.openUrlExternally(url)
    }

    ColumnLayout {
        Layout.fillWidth: true
        spacing: 20

        Frame {
            Layout.fillWidth: true
            padding: 24

            RowLayout {
                width: parent.width
                spacing: 20

                Rectangle {
                    Layout.preferredWidth: 96
                    Layout.preferredHeight: 96
                    Layout.alignment: Qt.AlignTop
                    radius: 24
                    color: Colors.proxy.backgroundColor
                    border.color: Colors.proxy.controlBorderColor
                    border.width: 1
                    clip: true

                    Skeleton {
                        anchors.fill: parent
                        radius: parent.radius
                        running: manifestLoading
                        visible: manifestLoading
                    }

                    Image {
                        id: pluginIcon
                        anchors.fill: parent
                        anchors.margins: 2
                        source: root.iconSource
                        fillMode: Image.PreserveAspectFit
                        asynchronous: true
                        visible: !manifestLoading

                        onStatusChanged: {
                            if (status === Image.Error)
                                root.iconSource = root.resourceUrl("default", "icon")
                        }
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 8

                    Text {
                        Layout.fillWidth: true
                        text: manifest && manifest.name ? manifest.name : qsTr("Loading plugin...")
                        typography: Typography.Title
                        wrapMode: Text.Wrap
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8

                        Text {
                            text: manifest && manifest.author ? manifest.author : qsTr("Unknown author")
                            typography: Typography.BodyStrong
                            color: Colors.proxy.primaryColor
                        }

                        Item { Layout.fillWidth: true }
                    }

                    Flow {
                        Layout.fillWidth: true
                        spacing: 8
                        visible: manifest && manifest.tags && manifest.tags.length > 0

                        Repeater {
                            model: manifest && manifest.tags ? manifest.tags : []

                            delegate: InfoBadge {
                                text: root.tagDisplayName(modelData)
                                severity: Severity.Info
                                solid: false
                            }
                        }
                    }

                    Text {
                        Layout.fillWidth: true
                        text: manifest && manifest.description ? manifest.description : ""
                        typography: Typography.Body
                        color: Colors.proxy.textSecondaryColor
                        wrapMode: Text.Wrap
                        maximumLineCount: 3
                        elide: Text.ElideRight
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8

                        Button {
                            highlighted: true
                            icon.name: "ic_fluent_arrow_download_20_regular"
                            text: qsTr("Download")
                            enabled: !!root.releasePageUrl()
                            onClicked: root.openUrl(root.releasePageUrl())
                        }

                        Button {
                            flat: true
                            icon.name: "ic_fluent_share_20_regular"
                            text: qsTr("Share")
                            onClicked: root.openUrl(root.baseUrl + "/plugins/" + encodeURIComponent(root.pluginId))
                        }
                    }
                }
            }
        }

        InfoBar {
            Layout.fillWidth: true
            visible: root.errorMessage.length > 0
            severity: Severity.Error
            title: qsTr("Load failed")
            text: root.errorMessage
        }

        GridLayout {
            Layout.fillWidth: true
            columns: width >= 980 ? 3 : 1
            columnSpacing: 20
            rowSpacing: 20

            ColumnLayout {
                Layout.fillWidth: true
                Layout.columnSpan: parent.columns === 3 ? 2 : 1
                Layout.alignment: Qt.AlignTop
                spacing: 20

                Frame {
                    Layout.fillWidth: true
                    padding: 24

                    ColumnLayout {
                        width: parent.width
                        spacing: 12

                        Text {
                            Layout.fillWidth: true
                            text: qsTr("Description")
                            typography: Typography.BodyLarge
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 1
                            color: Colors.proxy.controlBorderColor
                        }

                        MarkdownViewer {
                            Layout.fillWidth: true
                            html: root.readmeHtml
                            loading: root.readmeLoading
                            onLinkActivated: function(link) {
                                root.openUrl(link)
                            }
                        }
                    }
                }

                Frame {
                    Layout.fillWidth: true
                    padding: 24

                    ColumnLayout {
                        width: parent.width
                        spacing: 12

                        Text {
                            Layout.fillWidth: true
                            text: qsTr("More information")
                            typography: Typography.BodyLarge
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 1
                            color: Colors.proxy.controlBorderColor
                        }

                        GridLayout {
                            Layout.fillWidth: true
                            columns: width >= 520 ? 2 : 1
                            columnSpacing: 20
                            rowSpacing: 16

                            Repeater {
                                model: [
                                    { icon: "ic_fluent_tag_20_regular", label: qsTr("Plugin ID"), value: manifest && manifest.id ? manifest.id : pluginId },
                                    { icon: "ic_fluent_info_20_regular", label: qsTr("Version"), value: manifest && manifest.version ? manifest.version : qsTr("Unknown") },
                                    { icon: "ic_fluent_code_20_regular", label: qsTr("API version"), value: manifest && manifest.api_version ? manifest.api_version : qsTr("Unknown") },
                                    { icon: "ic_fluent_branch_20_regular", label: qsTr("Branch"), value: manifest && manifest.branch ? manifest.branch : "main" },
                                    { icon: "ic_fluent_person_20_regular", label: qsTr("Author"), value: manifest && manifest.author ? manifest.author : qsTr("Unknown") },
                                    { icon: "ic_fluent_link_20_regular", label: qsTr("Repository"), value: root.repoUrl() || qsTr("No data") }
                                ]

                                delegate: RowLayout {
                                    Layout.fillWidth: true
                                    spacing: 10

                                    Icon {
                                        Layout.alignment: Qt.AlignTop
                                        name: modelData.icon
                                        size: 20
                                        color: Colors.proxy.textSecondaryColor
                                    }

                                    ColumnLayout {
                                        Layout.fillWidth: true
                                        spacing: 2

                                        Text {
                                            Layout.fillWidth: true
                                            text: modelData.label
                                            typography: Typography.Caption
                                            color: Colors.proxy.textSecondaryColor
                                        }

                                        Text {
                                            Layout.fillWidth: true
                                            text: modelData.value
                                            wrapMode: Text.Wrap
                                            elide: Text.ElideRight
                                            maximumLineCount: 2
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

            Frame {
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignTop
                padding: 24

                ColumnLayout {
                    width: parent.width
                    spacing: 12

                    RowLayout {
                        Layout.fillWidth: true

                        Text {
                            Layout.fillWidth: true
                            text: qsTr("Discover more")
                            typography: Typography.BodyLarge
                        }

                        Button {
                            flat: true
                            visible: manifest && manifest.tags && manifest.tags.length > 0
                            text: qsTr("More")
                            icon.name: "ic_fluent_open_20_regular"
                            onClicked: root.openUrl(root.baseUrl + "/search?q=" + encodeURIComponent(root.tagId(manifest.tags[0])))
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 1
                        color: Colors.proxy.controlBorderColor
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 8
                        visible: !otherPluginsLoading && otherPlugins.length > 0

                        Repeater {
                            model: otherPlugins

                            delegate: PluginCard {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 82
                                plugin: modelData
                                transparentNormalBackground: true
                            }
                        }
                    }

                    Skeleton {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 250
                        running: otherPluginsLoading
                        visible: otherPluginsLoading
                    }

                    Text {
                        Layout.fillWidth: true
                        visible: !otherPluginsLoading && otherPlugins.length === 0
                        text: qsTr("No recommendations")
                        horizontalAlignment: Text.AlignHCenter
                        color: Colors.proxy.textSecondaryColor
                    }
                }
            }
        }
    }
}
