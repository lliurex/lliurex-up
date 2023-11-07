import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import org.kde.kirigami 2.16 as Kirigami

Rectangle{
    visible: true
    color:"transparent"

    GridLayout{
        id: loadGrid
        rows: 1
        rowSpacing:10
        flow: GridLayout.TopToBottom
        anchors.centerIn:parent

        Kirigami.InlineMessage {
            id: errorLabel
            visible:true
            text:getErrorText(unlockStackBridge.lockedService,mainStackBridge.showErrorMessage[0])
            type:{
                if (mainStackBridge.showErrorMessage[1]=="Warning"){
                    Kirigami.MessageType.Warning;
                }else{
                    Kirigami.MessageType.Error;
                }
            }
            Layout.minimumWidth:770
            Layout.fillWidth:true
            Layout.rightMargin:15
            Layout.leftMargin:15
        }
       
    }

    function getErrorText(service,code){

        var msg=""
        switch (code){
            case -1:
                msg=i18nd("lliurex-up","The unlocking process has failed");
                break;
            case 2:
                msg=service+" "+i18nd("lliurex-up","is now running. Wait a moment and try again")
                break;
            case 2:
                msg=i18nd("lliurex-up","Some process are running. Wait a moment and try again")
                break;
        }
        return msg
    }
}
