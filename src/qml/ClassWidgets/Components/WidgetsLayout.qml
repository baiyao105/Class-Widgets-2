import QtQuick
import QtQuick.Controls
import RinUI
import ClassWidgets.Easing

/*
 * WidgetsLayout —— 小组件横向排布（水平 ListView）
 *
 * 位置完全交给 ListView，本文件只做两件事：
 *   1. 把 contentWidth / contentHeight 正确算出来给容器用；
 *   2. 提供拖拽排序的落点计算。
 *
 * 注意：水平 ListView 的 contentHeight 等于它自己的 height（它只横向滚动），
 * 所以不能用它来当内容高度，否则会与 ListView.height 形成循环绑定。
 * 这里改成显式遍历 delegate 求最大高度。
 */
Item {
    id: layoutRoot

    // Python 端按该 objectName 查找布局并计算窗口点击区域
    objectName: "widgetsFlow"

    property bool editMode: false
    property bool hide: false
    property real scaleFactor: 1.0
    property real spacing: 8

    // 视口取得足够大，保证全部 delegate 都实例化而不被回收销毁，
    // 否则小组件会被反复重载。高度只需覆盖小组件的最高尺寸。
    property real viewportWidth: 100000
    property real viewportHeight: 4096

    readonly property alias count: listView.count
    readonly property real contentWidth: listView.contentWidth
    property real contentHeight: 0

    width: contentWidth
    height: contentHeight
    implicitWidth: contentWidth
    implicitHeight: contentHeight

    signal geometryChanged()
    signal editRequested()
    signal menuVisibilityChanged(bool visible)

    // 遍历 delegate 求最大高度。水平 ListView 不负责纵向布局，
    // 必须自己算，否则容器高度为 0、外层按钮会压在小组件上。
    function refreshContentHeight() {
        var tallest = 0
        for (var i = 0; i < listView.count; ++i) {
            var it = listView.itemAtIndex(i)
            if (it && it.visible && it.height > tallest)
                tallest = it.height
        }
        contentHeight = tallest
    }

    // 每帧最多向外通知一次几何变化，避免逐帧刷 Python 端 mask
    Timer {
        id: geometryCoalesce
        interval: 0
        repeat: false
        onTriggered: layoutRoot.geometryChanged()
    }

    function notifyGeometry() {
        geometryCoalesce.restart()
    }

    // 编辑模式拖拽落点：比较中心点，兼容不同宽度
    function dropIndex(draggedItem, fromIndex) {
        var center = draggedItem.x + draggedItem.dragOffsetX + draggedItem.width / 2
        var target = 0
        for (var i = 0; i < listView.count; ++i) {
            if (i === fromIndex)
                continue
            var it = listView.itemAtIndex(i)
            if (it && center > it.x + it.width / 2)
                ++target
        }
        return target
    }

    function moveWidget(fromIndex, toIndex) {
        WidgetsModel.moveInstance(fromIndex, toIndex)
    }

    // 供 delegate 判断后续是否还有可见小组件（决定是否需要输出间距）
    function itemAt(i) {
        return listView.itemAtIndex(i)
    }

    ListView {
        id: listView

        width: layoutRoot.viewportWidth
        height: layoutRoot.viewportHeight

        orientation: Qt.Horizontal
        spacing: 0
        interactive: false
        boundsBehavior: Flickable.StopAtBounds
        clip: false

        model: WidgetsModel

        // 增删都通过 delegate 自身的宽度动画完成，位置变化是连续的，
        // 因此不需要 add/remove 的 displaced 过渡（启用反而会与宽度动画互相重定向）。
        // 拖拽排序则是离散的模型 move，必须开启 move 的 displaced 过渡，
        // 否则只有被拖的项在动、被挤移的邻居会瞬间跳位。
        // 用弹簧曲线 popBack：被拖落的项落位时带轻微 overshoot，更灵动。
        move: Transition {
            NumberAnimation {
                properties: "x,y"
                duration: 260
                easing.type: Easing.Bezier
                easing.bezierCurve: BezierCurve.popBack
            }
        }
        addDisplaced: Transition { enabled: false }
        removeDisplaced: Transition { enabled: false }
        displaced: Transition {
            NumberAnimation {
                properties: "x,y"
                duration: 260
                easing.type: Easing.Bezier
                easing.bezierCurve: BezierCurve.popBack
            }
        }

        delegate: WidgetsLayoutDelegate {
            host: layoutRoot
            settingsDialog: settingsDialogInstance
        }

        onContentWidthChanged: {
            layoutRoot.notifyGeometry()
            layoutRoot.refreshContentHeight()
        }
        onCountChanged: layoutRoot.refreshContentHeight()
    }

    WidgetSettingsDialog {
        // 独立 id，避免与 delegate 的同名属性形成自引用
        id: settingsDialogInstance
    }

    Component.onCompleted: refreshContentHeight()
}