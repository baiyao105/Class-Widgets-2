import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects
import RinUI
import Widgets


Item {
    id: widgetBase
    // 最小宽度 = 内容 + 边距，默认可以被拉伸
    implicitWidth: Math.max(headerRow.implicitWidth, contentArea.implicitWidth) + 48
    Layout.minimumWidth: implicitWidth
    height: 100
    clip: true

    // colors
    property color backgroundColor: Theme.isDark()
        ? Qt.alpha("#1E1D22", 0.6)
        : Qt.alpha("#FBFAFF", 0.6)
    property color borderColor: Theme.isDark()
        ? Qt.alpha("#fff", 0.4)
        : Qt.alpha("#fff", 1)

    // properties
    property alias text: subtitleLabel.text
    property alias subtitle: subtitleArea.children
    property alias actions: actionButtons.children
    default property alias content: contentArea.children

    // 背景
    readonly property int borderWidth: 1

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

            Item { Layout.fillWidth: true } // 占位符，推开右侧按钮

            RowLayout {
                id: actionButtons
                Layout.fillHeight: true
                // 这里可以放按钮
            }
        }

        // 内容区
        Item {
            id: contentArea
            Layout.fillWidth: true
            Layout.fillHeight: true
            // implicitWidth: contentText.implicitWidth
            implicitWidth: {
                let maxRight = 0
                for (let i = 0; i < contentArea.children.length; i++) {
                    let child = contentArea.children[i];
                    if (!child.visible) continue;
                    let rightEdge = child.x + child.width;
                    if (rightEdge > maxRight)
                        maxRight = rightEdge;
                }
                return maxRight;
            }
        }
    }
}
