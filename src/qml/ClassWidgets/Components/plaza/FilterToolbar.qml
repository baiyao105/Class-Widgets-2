import QtQuick
import QtQuick.Layouts
import RinUI

RowLayout {
    id: root

    property var tags: []
    property string selectedTag: ""
    property string sortValue: "latest"
    property bool showRelevance: false
    property bool busy: false
    property var menuTags: []
    property bool openMenuWhenReady: false
    signal tagSelected(string tagId)
    signal sortSelected(string sortValue)

    readonly property var tagItems: root.tags instanceof Array ? root.tags : []
    readonly property int visibleTagCount: {
        var availableWidth = Math.max(120, root.width - 216)
        var usedWidth = root.estimatedTagWidth(qsTr("All"))
        var count = 0

        for (var i = 0; i < root.tagItems.length; ++i) {
            var tag = root.tagItems[i]
            var label = tag.name || tag.id || ""
            var nextWidth = root.estimatedTagWidth(label)
            if (usedWidth + nextWidth > availableWidth)
                break
            usedWidth += nextWidth
            ++count
        }

        return Math.max(1, count)
    }
    readonly property var baseVisibleTags: root.tagItems.slice(0, root.visibleTagCount)
    readonly property var activeHiddenTag: root.selectedTag === "" ? null : root.hiddenSelectedTag()
    readonly property var visibleTags: root.activeHiddenTag && root.baseVisibleTags.length > 0
        ? root.baseVisibleTags.slice(0, -1).concat([root.activeHiddenTag])
        : root.baseVisibleTags
    readonly property var hiddenTags: root.remainingTags()
    readonly property int selectedTagIndex: root.visibleTagIndex() + 1

    function tagId(tag) {
        return tag.id || tag.name || ""
    }

    function estimatedTagWidth(label) {
        return Math.ceil(String(label).length * 14 + 32)
    }

    function openMoreTagsMenu() {
        moreTagsMenu.close()
        menuTags = hiddenTags.slice()
        openMenuWhenReady = menuTags.length > 0
        openMoreTagsWhenReady()
    }

    function openMoreTagsWhenReady() {
        if (openMenuWhenReady && moreTagsMenu.count === menuTags.length) {
            openMenuWhenReady = false
            moreTagsMenu.open()
        }
    }

    function visibleTagIndex() {
        for (var i = 0; i < root.visibleTags.length; ++i) {
            if (root.tagId(root.visibleTags[i]) === root.selectedTag)
                return i
        }
        return -1
    }

    function hiddenSelectedTag() {
        for (var i = 0; i < root.tagItems.length; ++i) {
            var tag = root.tagItems[i]
            if (root.tagId(tag) === root.selectedTag && i >= root.baseVisibleTags.length)
                return tag
        }
        return null
    }

    function isVisibleTag(tag) {
        var id = root.tagId(tag)
        for (var i = 0; i < root.visibleTags.length; ++i) {
            if (root.tagId(root.visibleTags[i]) === id)
                return true
        }
        return false
    }

    function remainingTags() {
        var result = []
        for (var i = 0; i < root.tagItems.length; ++i) {
            if (!root.isVisibleTag(root.tagItems[i]))
                result.push(root.tagItems[i])
        }
        return result
    }

    spacing: 8

    RowLayout {
        spacing: 4

        SelectorBar {
            id: tagSelector
            enabled: !root.busy
            currentIndex: root.selectedTagIndex

            SelectorBarItem {
                text: qsTr("All")
                onClicked: root.tagSelected("")
            }

            Repeater {
                model: root.visibleTags

                delegate: SelectorBarItem {
                    width: implicitWidth
                    required property var modelData
                    readonly property string tagId: root.tagId(modelData)
                    text: modelData.name || modelData.id || ""
                    onClicked: root.tagSelected(tagId)
                }
            }
        }

        ToolButton {
            visible: root.hiddenTags.length > 0
            enabled: !root.busy
            flat: true
            icon.name: "ic_fluent_more_horizontal_20_regular"
            onClicked: root.openMoreTagsMenu()

            ToolTip {
                visible: parent.hovered
                text: qsTr("More categories")
            }

            Menu {
                id: moreTagsMenu
                height: implicitHeight

                // RinUI's default enter transition snapshots implicitHeight before
                // dynamically inserted menu items have completed layout.
                enter: Transition {
                    NumberAnimation {
                        property: "opacity"
                        from: 0
                        to: 1
                        duration: 100
                    }
                }
            }
        }

        Instantiator {
            id: tagMenuItems
            model: root.menuTags

            delegate: MenuItem {
                required property var modelData
                text: modelData.name || modelData.id || ""
                onTriggered: {
                    root.tagSelected(root.tagId(modelData))
                    moreTagsMenu.close()
                }
            }

            onObjectAdded: function(index, object) {
                moreTagsMenu.insertItem(index, object)
                root.openMoreTagsWhenReady()
            }

            onObjectRemoved: function(index, object) {
                moreTagsMenu.removeItem(object)
            }
        }
    }

    Item { Layout.fillWidth: true }

    DropDownButton {
        Layout.alignment: Qt.AlignRight
        enabled: !root.busy
        text: root.sortValue === "relevance" ? qsTr("Relevance")
            : root.sortValue === "name" ? qsTr("Name")
            : root.sortValue === "rating" ? qsTr("Rating")
            : root.sortValue === "downloads" ? qsTr("Downloads")
            : qsTr("Latest")
        icon.name: "ic_fluent_arrow_sort_20_regular"

        MenuItem { visible: root.showRelevance; text: qsTr("Relevance"); onTriggered: root.sortSelected("relevance") }
        MenuItem { text: qsTr("Latest"); onTriggered: root.sortSelected("latest") }
        MenuItem { text: qsTr("Name"); onTriggered: root.sortSelected("name") }
        MenuItem { text: qsTr("Rating"); onTriggered: root.sortSelected("rating") }
        MenuItem { text: qsTr("Downloads"); onTriggered: root.sortSelected("downloads") }
    }
}
