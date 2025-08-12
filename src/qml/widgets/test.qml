import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI
import Widgets


Widget {
    id: root
    text: "Hello World"
    Button {
        text: "Click me"
        onClicked: hello_world.sayHello()
    }

    Component.onCompleted: {
        console.log("wssb")
    }
}