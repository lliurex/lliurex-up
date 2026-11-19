import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    color: "transparent"

    ColumnLayout {
        id: mainContent
        anchors.fill: parent
        anchors.leftMargin: 5
        anchors.bottomMargin: 15
        spacing: 10

        Text { 
            text: i18nd("lliurex-up","Update information")
            font.pointSize: 16
        }

        GridLayout {
            id: infoLayout
            columns: 2
            rowSpacing: 10
            Layout.topMargin: 5
            Layout.alignment: Qt.AlignHCenter

            Text {
                id: currentVersionText
                Layout.alignment: Qt.AlignRight
                text: i18nd("lliurex-up","Current version:")
                font.pointSize: 10
            }

            Text {
                id: currentVersionValue
                text: infoStackBridge.versionInfo.currentVersion != null 
                        ? infoStackBridge.versionInfo.currentVersion : i18nd("lliurex-up","Not available")
                color: infoStackBridge.versionInfo.currentVersion != null ? "black" : "red"
                font.pointSize: 10
                Layout.alignment: Qt.AlignLeft
            }

            Text {
                id: availableVersionText
                Layout.alignment: Qt.AlignRight
                text: i18nd("lliurex-up","Available version (lliurex.gva.es):")
                font.pointSize: 10
            }

            Text {
                id: availableVersionValue
                text: infoStackBridge.versionInfo.availableVersion != null
                        ? infoStackBridge.versionInfo.availableVersion
                        : i18nd("lliurex-up","Not available. Check conexion to lliurex.gva.es")
                color: infoStackBridge.versionInfo. availableVersion != null ? "black" : "red"
                font.pointSize: 10
                Layout.alignment: Qt.AlignLeft
            }

            Text {
                id: candiateVersionText
                Layout.alignment: Qt.AlignRight
                text: i18nd("lliurex-up","Candidate version (to install):")
                font.pointSize: 10
            }

            Text {
                id: candiateVersionValue
                text: infoStackBridge.versionInfo.candidateVersion != null
                        ? infoStackBridge.versionInfo.candidateVersion
                        : i18nd("lliurex-up","Not available")
                color: infoStackBridge.versionInfo.candidateVersion != null ? "black" : "red"
                font.pointSize: 10
                Layout.alignment: Qt.AlignLeft
            }

            Text {
                id: numberPackagesText
                visible: mainStackBridge.updateRequired
                Layout.alignment:Qt.AlignRight
                text: i18nd("lliurex-up","Number of packages:")
                font.pointSize: 10
            }

            Text {
                id: numberPackagesValue
                visible: mainStackBridge.updateRequired
                text: infoStackBridge.packagesInfo.totalPackages+" ( "+infoStackBridge.packagesInfo.newPackages + " " + i18nd("lliurex-up","news") + " )"
                font.pointSize: 10
                Layout.alignment: Qt.AlignLeft
            }

            Text {
                id: sizeText
                visible: mainStackBridge.updateRequired
                Layout.alignment: Qt.AlignRight
                text: i18nd("lliurex-up","Size of update (aprox):")
                font.pointSize: 10
            }

            Text {
                id: sizeValue
                text: infoStackBridge.packagesInfo.upgradeSize
                visible: mainStackBridge.updateRequired
                font.pointSize: 10
                Layout.alignment: Qt.AlignLeft
            }

            Text {
                id: sourceText
                text: i18nd("lliurex-up","Update source:")
                font.pointSize: 10
                Layout.alignment: Qt.AlignRight
            }

            Text {
                id: sourceTextValue
                text: infoStackBridge.packagesInfo.updateSource != ""
                        ? infoStackBridge.packagesInfo.updateSource
                        : i18nd("lliurex-up","Not available")
                color: infoStackBridge.packagesInfo.updateSource != "" ? "black" : "red"
                font.pointSize: 10
                Layout.alignment: Qt.AlignLeft
            }

            Text {
                id: flatpakText
                text: i18nd("lliurex-up","Flatpak update info:")
                font.pointSize: 10
                Layout.alignment: Qt.AlignRight
                visible: infoStackBridge.flatpakInfo.totalFlatpak > 0 ? true : false
            }

            Text{
                id: flatpakValue
                text: i18nd("lliurex-up","Number of flapak:")+"  "+infoStackBridge.flatpakInfo.totalFlatpak+" - "+i18nd("lliurex-up","Size:")+ " < "+infoStackBridge.flatpakInfo.size
                font.pointSize: 10
                Layout.alignment: Qt.AlignRight
                visible: infoStackBridge.flatpakInfo.totalFlatpa > 0 ? true : false
            }
        }

        Item {
            Layout.fillHeight: true
        }
    }
}
