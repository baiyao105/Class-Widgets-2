import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI

ColumnLayout {
    Layout.fillWidth: true
    Text {
        typography: Typography.BodyStrong
        text: "Overview"
    }
    SettingExpander {
        Layout.fillWidth: true
        icon: "ic_fluent_info_20_regular"
        title: "Overview"
        description: "Class Widgets 2 | " + AppCentral.globalConfig.app.version

        SettingItem {
            title: "Version"
            // 此 SettingItem 没有描述
            content: Text {
                text: AppCentral.globalConfig.app.version
            }
        }
    }

    SettingCard {
        Layout.fillWidth: true
        icon: "ic_fluent_document_bullet_list_off_20_regular"
        title: qsTr("No Logs")
        description: qsTr("Do not save logs to local storage.")

        // Control placed on the right side via the 'content' default property
        Switch { // This Switch is assigned to the 'content' property
            checked: true
        }
    }
}