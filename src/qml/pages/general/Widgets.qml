import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI
import Qt5Compat.GraphicalEffects


FluentPage {
    title: qsTr("Widgets")

    Row {
        id: widgetsContainer
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 10
        Repeater {
            id: widgetRepeater
            model: WidgetModel

            delegate: Item {
                id: widgetContainer
                width: loader.width
                height: loader.height

                Loader {
                    id: loader
                    source: qmlPath
                    asynchronous: true
                    property int delay

                    onStatusChanged: {
                        if (status === Loader.Ready && item) {
                            if (item && backendObj) item.backend = backendObj
                            Qt.callLater(function () {
                                anim.start()
                            })
                        }
                    }
                }

                SequentialAnimation {
                    id: anim
                    NumberAnimation {
                        target: widgetContainer
                        property: "opacity"
                        from: 0;
                        to: 0; duration: 1
                    }
                    PauseAnimation {
                        duration: index * 125
                    }
                    ParallelAnimation {
                        NumberAnimation {
                            target: widgetContainer
                            property: "opacity"
                            from: 0;
                            to: 1; duration: 300
                            easing.type: Easing.OutCubic
                        }
                        NumberAnimation {
                            target: widgetContainer;
                            property: "scale";
                            from: 0.8;
                            to: 1; duration: 400;
                            easing.type: Easing.OutBack
                        }
                    }
                }
            }
        }
    }
}