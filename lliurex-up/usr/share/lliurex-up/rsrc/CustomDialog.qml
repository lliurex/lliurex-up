import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs 1.3
import org.kde.plasma.components 3.0 as PC3


Dialog {
    id: customDialog
    property alias dialogTitle:customDialog.title
    property alias dialogVisible:customDialog.visible
    property alias dialogMsg:dialogText.text
    property alias dialogWidth:container.implicitWidth
    signal dialogApplyClicked
    signal rejectDialogClicked
    property bool xButton

    visible:dialogVisible
    title:dialogTitle
    modality:Qt.WindowModal

    onVisibleChanged:{
        if (!this.visible && xButton){
            if ((loadStackBridge.showMirrorDialog)||(loadStackBridge.showRepoDialog)){
                rejectDialogClicked()
            }
        }else{
            xButton=true
        }
    }

    contentItem: Rectangle {
        id:container
        color: "#ebeced"
        implicitWidth: dialogWidth
        implicitHeight: 120
        anchors.topMargin:5
        anchors.leftMargin:5

        Image{
            id:dialogIcon
            source:"/usr/share/icons/breeze/status/64/dialog-question.svg"

        }
        
        Text {
            id:dialogText
            text:dialogMsg
            font.pointSize: 11
            anchors.left:dialogIcon.right
            anchors.verticalCenter:dialogIcon.verticalCenter
            anchors.leftMargin:10
        
        }
      
        PC3.Button {
            id:dialogApplyBtn
            display:AbstractButton.TextBesideIcon
            icon.name:"dialog-ok"
            text: i18nd("lliurex-up","Yes")
            focus:true
            visible:true
            font.pointSize: 11
            anchors.bottom:parent.bottom
            anchors.right:dialogCancelBtn.left
            anchors.rightMargin:10
            anchors.bottomMargin:5

            Keys.onReturnPressed: dialogApplyBtn.clicked()
            Keys.onEnterPressed: dialogApplyBtn.clicked()
            onClicked:{
                xButton:false
                dialogApplyClicked()
            }
            
        }

        PC3.Button {
            id:dialogCancelBtn
            display:AbstractButton.TextBesideIcon
            icon.name:"dialog-cancel"
            text: i18nd("lliurex-up","No")
            focus:true
            font.pointSize: 11
            anchors.bottom:parent.bottom
            anchors.right:parent.right
            anchors.rightMargin:5
            anchors.bottomMargin:5
            Keys.onReturnPressed: dialogCancelBtn.clicked()
            Keys.onEnterPressed: dialogCancelBtn.clicked()
            onClicked:{
                xButton:false
                rejectDialogClicked()

            }
        
        }
     
    }
 }
