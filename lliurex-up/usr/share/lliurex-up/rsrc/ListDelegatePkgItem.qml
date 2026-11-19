import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQml.Models
import org.kde.kirigami as Kirigami

ItemDelegate {
    id: listPkgItem
    property string pkgId
    property string pkgVersion
    property string pkgSize
    property string pkgIcon
    property int pkgStatus
    property bool showStatus

    enabled: true
    height: 60

    width: listPkgItem.ListView.view ? listPkgItem.ListView.view.width-10 : 0
    hoverEnabled: true
    leftPadding: 15
    rightPadding: 10

    onHoveredChanged: {
        if (listPkgItem.ListView.view){
            if (hovered){
                listPkgItem.ListView.view.currentIndex=index
            }
        }else if (!hovered && listPkgItem.ListView.view.currentIndex === index){
            listPkgItem.ListView.view.currentIndex = -1
        }
    }

    background: Rectangle {
        x: 5
        y: 5
        width: parent.width - 5
        height: parent.height - 5

        color: listPkgItem.hovered ? Qt.alpha(Kirigami.Theme.highlightColor,0.15) : "transparent"
    
        radius: 6
        border.width: 1
        border.color: listPkgItem.hovered ? Kirigami.Theme.highlightColor : "transparent"
    }

    contentItem: RowLayout {
        id: pkgItem
        spacing: 20

        Image {
            id: packageIcon
            source: pkgIcon
            Layout.preferredWidth: 35
            Layout.preferredHeight: 35
            fillMode:Image.PreserveAspectFit
        } 

        ColumnLayout {
            id: pkgDescription
            spacing:10
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignVCenter
            Layout.preferredWidth: 0

            Text {
                id: pkgName
                text: pkgId
                elide:Text.ElideMiddle
                font.pointSize: 11
                horizontalAlignment: Text.AlignLeft
                Layout.fillWidth: true
            }

            Text {
                id: packageVersion
                text: pkgVersion
                elide: Text.ElideMiddle
                font.pointSize: 10
                horizontalAlignment: Text.AlignLeft
                Layout.fillWidth: true
            }
        }

        Text {
            id: packageSize
            text: pkgSize
            Layout.alignment: Qt.AlingRight | Qt.AlignVCenter
        }

        Kirigami.Icon {
            id: statusImg
            source: listPkgItem.pkgStatus === 0 ? "data-success" : "data-error"
            visible: listPkgItem.showStatus ? true : false
            Layout.preferredWidth: 32
            Layout.preferredHeight: 32
            Layout.alignment: Qt.AlignVCenter
        }

        Button{
            id: showChangelogBtn
            display: AbstractButton.IconOnly
            icon.name: "help-about"
            Layout.alignment: Qt.AlignVCenter
            Layout.preferredWidth: visible ? implicitWidth : 0
            visible: listPkgItem.hovered  && mainStackBridge.endProcess ? true:false

            ToolTip {
                id: showChangelogToolTip
                delay: 1000
                timeout: 3000
                visible: showChangelogBtn.hovered
                text: i18nd("lliurex-up","Press to view pkg changelog")
                background: Rectangle {
                    color: "#ffffff"
                    border.color: "#b8b9ba"
                    radius: 5.0
                }
            }
            onClicked: {
                packageStackBridge.showPkgChangelog(pkgId)
                changelogPopUp.open()
            }
        }
    }
}
