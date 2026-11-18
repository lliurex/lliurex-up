import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window
import org.kde.plasma.core as PlasmaCore
import org.kde.kirigami as Kirigami

ApplicationWindow {
    id: window
    visible: true
    title: "LliureX-Up"
    property int margin: 10
    color: "#eff0f1"

    width: 620
    height: mainLayout.implicitHeight + 2 * margin
    minimumWidth: 620
    maximumWidth: 620
    minimumHeight: mainLayout.implicitHeight + 2 * margin
    maximumHeight: mainLayout.implicitHeight + 2 * margin

    Component.onCompleted: {
        x = Screen.width / 2 - width / 2
        y = Screen.height / 2 - height / 2
    }

    onClosing: (close) => {
        close.accepted = launchStackBridge.closed(true)
    }

    ColumnLayout {
        id: mainLayout
        anchors.fill: parent
        anchors.margins: margin
        spacing: 10

        GridLayout {
            id: grid
            Layout.fillWidth: true
            columns: 2
            columnSpacing: 15
            rowSpacing: 10

            Kirigami.Icon {
                id: iconInternal
                source:"dialog-warning"
                Layout.preferredWidth: Kirigami.Units.iconSizes.huge
                Layout.preferredHeight: Kirigami.Units.iconSizes.huge
            }

            Text {
                id: warningText
                text: getText()
                font.pointSize: 11
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignVCenter
            }

            Item {
                Layout.columnSpan: 2
                Layout.fillWidth: true
                Layout.preferredHeight: 25
                visible: launchStackBridge.isProgressBarVisible

                ProgressBar {
                    id: feedBackBar
                    indeterminate: true
                    implicitWidth: 250
                    anchors.centerIn: parent
                }
            }

            RowLayout {
                id: btnBox
                visible: !launchStackBridge.isProgressBarVisible
                Layout.columnSpan: 2
                Layout.fillWidth: true
                Layout.topMargin: 5
                spacing: 15

                Item { Layout.fillWidth: true }

                Button {
                    id: applyBtn
                    display: AbstractButton.TextBesideIcon
                    icon.name: "dialog-ok"
                    text: i18nd("lliurex-up", "Yes")
                    visible: launchStackBridge.showApplyBtn
                    Keys.onReturnPressed: applyBtn.clicked()
                    Keys.onEnterPressed: applyBtn.clicked()
                    onClicked: launchStackBridge.launchUnlockProcess()
                }

                Button {
                    id: cancelBtn
                    display: AbstractButton.TextBesideIcon
                    icon.name: launchStackBridge.showApplyBtn ? "dialog-cancel" : "dialog-close"
                    text: launchStackBridge.showApplyBtn ? i18nd("lliurex-up", "No") : i18nd("lliurex-up", "Close")
                    Keys.onReturnPressed: cancelBtn.clicked()
                    Keys.onEnterPressed: cancelBtn.clicked()
                    onClicked:  window.close()
                }
            }
        }
    }

    function getText() {

        switch (launchStackBridge.dialogTextCode) {
            case 1:
                return launchStackBridge.lockedService + " " + i18nd("lliurex-up", "is now running. Wait a moment and try again")
            case 2:
                return i18nd("lliurex-up", "Some process are running. Wait a moment and try again")
            case 3:
                return launchStackBridge.lockedService + " " + i18nd("lliurex-up", "seems blocked by a failed previous execution.\nLliurex-Up can not continue if this block is maintained.\nDo you want to try to unlock it?")
            case 4:
                return i18nd("lliurex-up", "The unlocking process is running. Wait a moment...")
            case -1:
                return i18nd("lliurex-up", "You need administration privileges to run this application.")
            case -2:
                return i18nd("lliurex-up", "The unlocking process has failed")
            default:
                return ""
        }

    }
}
