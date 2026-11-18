import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Popup {
    id: changelogPopUp
    width: 600
    height: 350
    anchors.centerIn: Overlay.overlay
    modal: true
    focus: true
    closePolicy: Popup.AutoClose
    padding: 15

    background: Rectangle {
        color: "#ebeced"
        border.color: "#b8b9ba"
        border.width: 1
        radius: 5.0
    }

    contentItem: ColumnLayout {
        id: mainContainer
        spacing: 15

        Text {
            id: changelogText
            text: i18nd("lliurex-up", "Changelog")
            font.pointSize: 16
            Layout.fillWidth: true
        }

        ScrollView {
            id: scrollView
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true

            Text {
                id: pkgChangelogText
                width: scrollView.availableWidth
                height: Math.max(implicitHeight, scrollView.availableHeight)

                readonly property bool isSearching: packageStackBridge.pkgChangelog.changelog === ""

                text: isSearching
                      ? i18nd("lliurex-up", "Searching changelog. Wait a moment...")
                      : packageStackBridge.pkgChangelog.changelog

                font.pointSize: 11
                horizontalAlignment: isSearching ? Text.AlignHCenter : Text.AlignLeft
                verticalAlignment: isSearching ? Text.AlignVCenter : Text.AlignTop
                wrapMode: Text.WordWrap
            }
        }

        RowLayout {
            Layout.fillWidth: true

            Item {
                Layout.fillWidth: true
            }

            Button {
                id: closeBtn
                focus: true
                display: AbstractButton.TextBesideIcon
                icon.name: "dialog-close"
                text: i18nd("lliurex-up", "Close")
                Keys.onReturnPressed: closeBtn.clicked()
                Keys.onEnterPressed: closeBtn.clicked()
                onClicked: changelogPopUp.close()
            }
        }
    }
}
