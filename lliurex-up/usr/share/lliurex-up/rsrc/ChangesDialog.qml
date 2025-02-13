import QtQuick      
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import org.kde.plasma.components as PC


Dialog {
    id: pendingChangesDialog
    property alias dialogVisible:pendingChangesDialog.visible
    property bool xButton
    
    signal dialogApplyClicked
    signal discardDialogClicked
    signal cancelDialogClicked

    visible:dialogVisible
    title:"Lliurex-Up -"+i18nd("lliurex-up","Settings")
    modal:true
    anchors.centerIn:Overlay.overlay
    background:Rectangle{
        color:"#ebeced"
        border.color:"#b8b9ba"
        border.width:1
        radius:5.0
    }
    
    onVisibleChanged:{
        if (!this.visible && xButton){
            if (settingStackBridge.showChangesDialog){
                cancelDialogClicked()
            }
        }else{
            xButton=true
        }
    }

    contentItem: Rectangle {
        color: "#ebeced"
        implicitWidth: 400
        implicitHeight: 130
        anchors.topMargin:5
        anchors.leftMargin:5

        Image{
            id:dialogIcon
            source:"/usr/share/icons/breeze/status/64/dialog-warning.svg"

        }
        
        Text {
            id:dialogText
            text:i18nd("lliurex-up","There are pending changes to apply.\nDo you want apply the changes or discard them?")
            font.family: "Quattrocento Sans Bold"
            font.pointSize: 10
            anchors.left:dialogIcon.right
            anchors.verticalCenter:dialogIcon.verticalCenter
            anchors.leftMargin:10
        
        }

        PC.Button {
            id:dialogApplyBtn
            display:AbstractButton.TextBesideIcon
            icon.name:"dialog-ok"
            text: i18nd("lliurex-up","Apply")
            focus:true
            font.family: "Quattrocento Sans Bold"
            font.pointSize: 10
            anchors.bottom:parent.bottom
            anchors.right:dialogDiscardBtn.left
            anchors.rightMargin:10
            anchors.bottomMargin:5
            DialogButtonBox.buttonRole: DialogButtonBox.ApplyRole
            Keys.onReturnPressed: dialogApplyBtn.clicked()
            Keys.onEnterPressed: dialogApplyBtn.clicked()
            onClicked:{
                xButton=false
                mainStackBridge.managePendingChangesDialog("Apply")
                dialogApplyClicked()
            }
        }

        PC.Button {
            id:dialogDiscardBtn
            display:AbstractButton.TextBesideIcon
            icon.name:"delete"
            text: i18nd("lliurex-up","Discard")
            focus:true
            font.family: "Quattrocento Sans Bold"
            font.pointSize: 10
            anchors.bottom:parent.bottom
            anchors.right:dialogCancelBtn.left
            anchors.rightMargin:10
            anchors.bottomMargin:5
            DialogButtonBox.buttonRole: DialogButtonBox.DestructiveRole
            Keys.onReturnPressed: dialogDiscardBtn.clicked()
            Keys.onEnterPressed: dialogDiscardBtn.clicked()
            onClicked:{
                xButton=false
                mainStackBridge.managePendingChangesDialog("Discard")
                discardDialogClicked()
            }
        }

        PC.Button {
            id:dialogCancelBtn
            display:AbstractButton.TextBesideIcon
            icon.name:"dialog-cancel"
            text: i18nd("lliurex-up","Cancel")
            focus:true
            font.family: "Quattrocento Sans Bold"
            font.pointSize: 10
            anchors.bottom:parent.bottom
            anchors.right:parent.right
            anchors.rightMargin:5
            anchors.bottomMargin:5
            DialogButtonBox.buttonRole:DialogButtonBox.RejectRole
            Keys.onReturnPressed: dialogCancelBtn.clicked()
            Keys.onEnterPressed: dialogCancelBtn.clicked()
            onClicked:{
                xButton:false
                cancelDialogClicked()
            }
        }
    }
   
 }
