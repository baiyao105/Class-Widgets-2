import QtQuick
import Qt5Compat.GraphicalEffects
import RinUI
import ClassWidgets.Easing


BaseWidget {
    id: root

    cornerRadius: Configs.data.preferences.widget_corner_radius
    backgroundColor: Theme.isDark()
        ? Qt.alpha("#1E1D22", 0.65)
        : Qt.alpha("#FBFAFF", 0.7)
    borderColor: Theme.isDark()
        ? Qt.alpha("#fff", 0.4)
        : Qt.alpha("#fff", 1)
    opacity: hoverHandler.hovered ? 0.8 : 1

    backgroundArea: Item {
        anchors.fill: parent

        Rectangle {
            anchors.fill: parent
            radius: root.cornerRadius
            color: root.backgroundColor
            opacity: Configs.data.preferences.opacity
        }

        Item {
            anchors.fill: parent

            Rectangle {
                id: borderRect
                anchors.fill: parent
                radius: root.cornerRadius
                layer.enabled: true
                layer.effect: LinearGradient {
                    start: Qt.point(0, 0)
                    end: Qt.point(width, height)
                    gradient: Gradient {
                        GradientStop { position: 0; color: root.borderColor }
                        GradientStop { position: 0.5; color: Qt.alpha("#fff", 0) }
                        GradientStop { position: 0.6; color: Qt.alpha("#fff", 0) }
                        GradientStop { position: 1; color: root.borderColor }
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
                    border.width: root.borderWidth
                }
            }
            opacity: Configs.data.preferences.opacity * 2
        }
    }

    HoverHandler {
        id: hoverHandler
    }

    Behavior on implicitWidth {
        NumberAnimation {
            duration: 400
            easing.type: Easing.Bezier
            easing.bezierCurve: BezierCurve.liquidBack
        }
    }

    Behavior on height {
        NumberAnimation {
            duration: 400
            easing.type: Easing.Bezier
            easing.bezierCurve: BezierCurve.liquidBack
        }
    }

    Behavior on backgroundColor {
        ColorAnimation {
            duration: 350
            easing.type: Easing.OutQuint
        }
    }

    Behavior on borderColor {
        ColorAnimation {
            duration: 250
            easing.type: Easing.OutQuint
        }
    }

    Behavior on opacity {
        NumberAnimation {
            duration: 200
            easing.type: Easing.InOutQuad
        }
    }
}
