import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI
import Widgets


Widget {
    id: root
    text: qsTr("测试组件")

    RowLayout {
        anchors.centerIn: parent
        spacing: 10
        Icon {
            icon: "ic_fluent_symbols_20_regular"
        }
        Button {
            text: "Open"
            onClicked: backend.sayHello(settings.name)
        }
    }
}