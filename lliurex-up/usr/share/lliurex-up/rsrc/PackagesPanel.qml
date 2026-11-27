import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: rectLayout
    color: "transparent"

    ColumnLayout {
        id: mainContent
        anchors.fill: parent
        anchors.leftMargin: 5
        anchors.bottomMargin: 15
        spacing: 10

        Text { 
            text: i18nd("lliurex-up","List of packages to update/install")
            font.pointSize: 16
        }

        PackagesList {
            id: packagesList
            Layout.fillHeight: true
            Layout.fillWidth: true
            packagesModel: packageStackBridge.packagesModel
        }
    }

    ChangelogPopUp {
        id: changelogPopUp
    }
} 
