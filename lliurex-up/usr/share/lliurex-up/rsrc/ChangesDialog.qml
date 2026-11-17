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
        implicitWidth: customDialog.dialogWidth
        implicitHeight: 140

        RowLayout {
            id: contentRow
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            spacing: 15

            Kirigami.Icon {
                id: iconInternal
                Layout.preferredWidth: Kirigami.Units.iconSizes.huge
                Layout.preferredHeight: Kirigami.Units.iconSizes.huge
            }
            
            Text {
                id: dialogText
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
                icon.name: "dialog-ok"
                onClicked: dialogApplyClicked()
            }

            Button {
                id: dialogDiscardBtn
                icon.name: "delete"
                onClicked: discardDialogClicked()
            }

            Button {
                id: dialogCancelBtn
                icon.name: "dialog-cancel"
                onClicked: rejectDialogClicked()
            }
        }
    }
} 
