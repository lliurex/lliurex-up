import QtQuick      
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami


Popup {
    id: pendingChangesDialog
    property bool dialogVisible: false
    visible: dialogVisible

    signal dialogApplyClicked
    signal discardDialogClicked
    signal rejectDialogClicked
    
    modal:true
    closePolicy:Popup.NoAutoClose
    anchors.centerIn:Overlay.overlay

    background: Rectangle {
        color: "#ebeced"
        border.color: "#b8b9ba"
        border.width: 1
        radius: 5
    }

    contentItem: Rectangle {
        id:container
        color: "#ebeced"
        implicitWidth: 400
        implicitHeight: 140

        RowLayout {
            id: contentRow
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            spacing: 15

            Kirigami.Icon {
                id: iconInternal
                source:"dialog-warning"
                Layout.preferredWidth: Kirigami.Units.iconSizes.huge
                Layout.preferredHeight: Kirigami.Units.iconSizes.huge
            }
            
            Text {
                id: dialogText
                text: i18nd("lliurex-up","There are pending changes to apply. Do you want apply or discard the changes")
                font.pointSize: 10
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                verticalAlignment: Text.AlignVCenter
                color: "#31363b"
            }
        }
        
        RowLayout {
            anchors.bottom: parent.bottom
            anchors.right: parent.right
            anchors.margins: 10
            spacing: 10

            Button {
                id: dialogApplyBtn
                text: i18nd("lliurex-up","Apply")
                icon.name: "dialog-ok"
                onClicked: dialogApplyClicked()
            }

            Button {
                id: dialogDiscardBtn
                text: i18nd("lliurex-up","Discard")
                icon.name: "delete"
                onClicked: discardDialogClicked()
            }

            Button {
                id: dialogCancelBtn
                text: i18nd("lliurex-up","Cancel")
                icon.name: "dialog-cancel"
                onClicked: rejectDialogClicked()
            }
        }
    }
} 
