import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects
import RinUI
import Widgets


Item {
    id: widgetBase
    // 最小宽度 = 内容 + 边距，默认可以被拉伸
    implicitWidth: Math.max(headerRow.implicitWidth, contentArea.childrenRect.width) + 48
    height: 100
    clip: true

    // colors
    property color backgroundColor: Theme.isDark()
        ? Qt.alpha("#1E1D22", 0.7)
        : Qt.alpha("#FBFAFF", 0.7)
    property color borderColor: Theme.isDark()
        ? Qt.alpha("#fff", 0.4)
        : Qt.alpha("#fff", 1)

    // backend
    property var backend: null

    // properties
    property alias text: subtitleLabel.text
    property alias subtitle: subtitleArea.children
    property alias actions: actionButtons.children
    default property alias content: contentArea.children

    // 背景
    readonly property int borderWidth: 1

    // 动画
    Behavior on implicitWidth {
        NumberAnimation { duration: 500; easing.type: Easing.OutBack }
    }

    // 渐变边框
    Item {
        anchors.fill: parent
        Rectangle {
            id: borderRect
            anchors.fill: parent
            radius: background.radius
            layer.enabled: true
            layer.effect: LinearGradient {
                start: Qt.point(0, 0)
                end: Qt.point(width, height)
                gradient: Gradient {
                    GradientStop { position: 0; color: borderColor }
                    GradientStop { position: 0.5; color: Qt.alpha("#fff", 0) }
                    GradientStop { position: 0.6; color: Qt.alpha("#fff", 0) }
                    GradientStop { position: 1; color: borderColor }
                }
            }
        }
        layer.enabled: true
        layer.effect: OpacityMask {
            maskSource: Rectangle {
                width: borderRect.width
                height: borderRect.height
                radius: borderRect.radius
                color: "transparent"
                border.width: borderWidth
            }
        }
        z: 1
    }

    // 内部背景矩形
    Rectangle {
        id: background
        anchors.fill: parent
        radius: 12
        color: backgroundColor
    }

    // 主布局
    ColumnLayout {
        id: mainLayout
        anchors.fill: parent
        anchors.topMargin: 16
        anchors.bottomMargin: 18
        anchors.leftMargin: 24
        anchors.rightMargin: 24
        spacing: 8

        // 顶部 subtitle + actions
        RowLayout {
            id: headerRow
            Layout.fillWidth: true
            spacing: 12

            RowLayout {
                id: subtitleArea
                Layout.fillHeight: true
                Subtitle {
                    id: subtitleLabel
                }
            }

            Item { Layout.fillWidth: true }

            RowLayout {
                id: actionButtons
                Layout.fillHeight: true
            }
        }

        // 内容区
        Item {
            id: contentArea
            Layout.fillWidth: true
            Layout.fillHeight: true
        }
    }
}
