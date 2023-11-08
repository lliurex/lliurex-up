import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs 1.3


Rectangle{
    visible: true
    color:"transparent"

    GridLayout{
        id: loadGrid
        rows: 3
        flow: GridLayout.TopToBottom
        anchors.centerIn:parent

        RowLayout{
            Layout.fillWidth: true
            Layout.alignment:Qt.AlignHCenter

            Rectangle{
                color:"transparent"
                width:30
                height:30
                
                AnimatedImage{
                    source: "/usr/share/lliurex-up/rsrc/loading.gif"
                    transform: Scale {xScale:0.45;yScale:0.45}
                }
            }
        }

        RowLayout{
            Layout.fillWidth: true
            Layout.alignment:Qt.AlignHCenter

            Text{
                id:loadtext
                text:{
                    if (loadStackBridge.loadStep==12){
                        getMsg()+" "+loadStackBridge.countDownValue+" "+i18nd("lliurex-up","seconds")
                    }else{
                        getMsg()
                    }
                }
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 10
                Layout.alignment:Qt.AlignHCenter
            }
        }

         RowLayout{
            Layout.fillWidth: true
            Layout.alignment:Qt.AlignHCenter

            ProgressBar{
                id:loadBar
                from:0.0
                to:1.0
                value:loadStackBridge.progressValue
                Layout.alignment:Qt.AlignHCenter
            }
        }
    }

    function getMsg(){

        var msg=""
        var headed=loadStackBridge.loadStep+" "+i18nd("lliurex-up","of")+" "+loadStackBridge.totalSteps
        switch(loadStackBridge.loadStep){
            case 1:
                msg=i18nd("lliurex-up","Checking sytem...")
                break;
            case 2:
                msg=i18nd("lliurex-up","Checking mirror...")
                break;
            case 3:
                msg=i18nd("lliurex-up","Executing init-actions...")
                break;
            case 4:
                msg=i18nd("lliurex-up","Looking for new version of Lliurex-Up...")
                break;
            case 5:
                msg=i18nd("lliurex-up","Updating Lliurex-Up...")
                break;
            case 6:
                msg=i18nd("lliurex-up","Checking if mirror exist and there is updated...")
                break;
            case 7:
                msg=i18nd("lliurex-up","Looking for new version to update...")
                break;
            case 8:
                msg=i18nd("lliurex-up","Looking for new version available...")
                break;
            case 9:
                msg=i18nd("lliurex-up","Checking if installation of metapackage is required...")
                break;
            case 10:
                msg=i18nd("lliurex-up","Looking for new updates...")
                break;
            case 12:
                msg=i18nd("lliurex-up","Lliurex-Up is now updated and will be reboot in ")
                return msg
        }
        msg=headed+". "+msg
        return msg
    }
}
