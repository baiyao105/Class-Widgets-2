import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Effects
import Qt5Compat.GraphicalEffects  // 图形库
import RinUI

Item {
    id: root

    property Component dynamicContent: null
    property alias icon: icon
    property string title: ""
    property string subtitle: ""
    // property bool backgroundVisible: false
    property Gradient backgroundGradient: Gradient {
        id: lightGradient
        GradientStop { position: 0.0; color: "#72BBCF" }
        GradientStop { position: 0.8; color: Qt.alpha("#F4F8F9", 0.5) }
    }
    property color accentColor: "#25a7ae"

    // 1. 定义亮色主题渐变
    // Gradient {
    //     id: lightGradient
    //     GradientStop { position: 0.0; color: "#72BBCF" }
    //     GradientStop { position: 0.8; color: Qt.alpha("#72BBCF", 0) }
    // }

    // 2. 定义暗色主题渐变
    // Gradient {
    //     id: darkGradient
    //     GradientStop { position: 0.0; color: Qt.alpha("#010A19", 0) }
    //     GradientStop { position: 1; color: Qt.alpha("#183672", 0.5) }
    // }

    Rectangle {
        id: background
        anchors.fill: parent
        color: "transparent"
        gradient: Theme.isDark() ? null : backgroundGradient
        visible: false
        // color: root.backgroundColor

        Image {
            anchors.fill: parent
            source: PathManager.images("tutorial/visual.png")
            fillMode: Image.PreserveAspectCrop
            visible: Theme.isDark()
            opacity: 0.5
        }
    }
    Item {
        id: backgroundBackdrop
        anchors.fill: parent

        OpacityMask {
            id: bannerContent
            anchors.fill: parent
            source: background
            maskSource: Rectangle {
                width: bannerContent.width
                height: bannerContent.height

                gradient: Gradient {
                    orientation: Gradient.Horizontal
                    GradientStop { position: 0; color: "transparent" }
                    GradientStop { position: 0.2; color: "white" }
                }
            }
        }
    }

    Loader {
        anchors.fill: parent
        sourceComponent: root.dynamicContent
        visible: root.dynamicContent !== null
    }

    Item {
        id: fallback
        anchors.fill: parent
        visible: root.dynamicContent === null

        Icon {
            id: icon
            size: 96
            anchors.centerIn: parent
            source: PathManager.images("icons/cw2_whatsnew.png")
        }
    }
}
