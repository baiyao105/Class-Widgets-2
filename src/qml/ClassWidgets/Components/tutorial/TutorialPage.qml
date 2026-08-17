import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI

Item {
    id: root
    transformOrigin: Item.Center

    property var tutorial
    property string title: ""
    property string description: ""
    property int currentStep: 1
    property int totalSteps: 1
    property bool allowBack: true
    property bool allowNext: true
    property string nextText: qsTr("Continue")
    property string nextIcon: "ic_fluent_arrow_right_20_regular"
    property real leftColumnRatio: 0.55
    property Component rightContent: null
    property alias icon: ricon
    property real pageTransitionOffset: 0

    default property alias operationContent: operationContentArea.data

    signal backRequested()
    signal nextRequested()

    function requestBack() {
        backRequested()
    }

    function requestNext() {
        nextRequested()
    }

    RowLayout {
        anchors.fill: parent

        spacing: 0

        ColumnLayout {
            id: leftArea
            // Layout.fillWidth: true
            Layout.preferredWidth: parent.width * leftColumnRatio
            Layout.fillHeight: true
            Layout.margins: 46
            Layout.leftMargin: 56
            Layout.rightMargin: 56
            spacing: 16

            Item {
                id: leftContentViewport
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true

                ColumnLayout {
                    id: leftContentArea
                    width: Math.min(parent.width, 600)
                    height: parent.height
                    anchors.verticalCenter: parent.verticalCenter
                    x: (parent.width - width) / 2 + root.pageTransitionOffset
                    spacing: 16

                    ColumnLayout {
                        spacing: 4
                        Text {
                            text: root.title
                            typography: Typography.Title
                        }

                        Text {
                            Layout.fillWidth: true
                            visible: root.description.length > 0
                            text: root.description
                            typography: Typography.Body
                            // color: Colors.proxy.textSecondaryColor
                            wrapMode: Text.WordWrap
                        }
                    }

                    Flickable {
                        id: leftOperationArea
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        contentWidth: width
                        contentHeight: Math.max(height, operationContentArea.implicitHeight)
                        flickableDirection: Flickable.VerticalFlick
                        boundsBehavior: Flickable.StopAtBounds

                        ColumnLayout {
                            id: operationContentArea
                            width: leftOperationArea.width
                            spacing: 0
                        }

                        ScrollBar.vertical: ScrollBar {
                            policy: ScrollBar.AsNeeded
                        }
                    }
                }
            }

            TutorialStepFooter {
                currentStep: root.currentStep
                totalSteps: root.totalSteps
                backVisible: root.allowBack
                nextEnabled: root.allowNext
                nextText: root.nextText
                nextIcon: root.nextIcon
                onBackRequested: root.requestBack()
                onNextRequested: root.requestNext()
            }
        }

        Item {
            Layout.fillWidth: true
            Layout.preferredWidth: parent.width * (1 - root.leftColumnRatio)
            Layout.fillHeight: true

            Loader {
                anchors.fill: parent
                sourceComponent: root.rightContent || defaultRightContent
            }
        }
    }

    Icon{
        id: ricon
        visible: false
        source: PathManager.images("icons/cw2_whatsnew.png")
    }

    Component {
        id: defaultRightContent

        TutorialVisual {
            anchors.fill: parent
            icon.name: ricon.name
            icon.source: ricon.source
        }
    }
}
