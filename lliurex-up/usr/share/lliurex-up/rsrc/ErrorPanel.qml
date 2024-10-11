import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

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
            text:getErrorText()
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

    function getErrorText(){

        var msg=""
        switch (mainStackBridge.showErrorMessage[0]){
            case -1:
                msg=i18nd("lliurex-up","There's not enough space on disk to upgrade (2 GB needed)");
                break;
            case -2:
                msg=i18nd("lliurex-up","Unable to connect to lliurex.net")
                break;
            case -3:
                msg=i18nd("lliurex-up","Mirror is being updated in server. Unable to update the system")
                break;
            case -4:
                msg=i18nd("lliurex-up","Unable to connect with server")
                break;
            case -5:
                msg=i18nd("lliurex-up","Unable to update Lliurex-Up. See /var/log/lliurex-up.log")+ " "+mainStackBridge.showErrorMessage[2]
                break;
            case -6:
                msg=i18nd("lliurex-up","Updated abort. An error occurred in the search for updates")+" "+mainStackBridge.showErrorMessage[2]
                break;
            case -7:
                msg=i18nd("lliurex-up","Updated abort for incorrect metapackages detected in update")
                break;
        }
        return msg
    }
}
