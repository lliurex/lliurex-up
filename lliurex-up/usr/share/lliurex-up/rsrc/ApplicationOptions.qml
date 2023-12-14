import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import org.kde.plasma.components 3.0 as PC3
import org.kde.kirigami 2.16 as Kirigami

GridLayout{
    id: optionsGrid
    columns: 2
    flow: GridLayout.LeftToRight
    columnSpacing:10

    Rectangle{
        width:190
        Layout.minimumHeight:460
        Layout.preferredHeight:460
        Layout.fillHeight:true
        border.color: "#d3d3d3"

        GridLayout{
            id: menuGrid
            rows:5 
            flow: GridLayout.TopToBottom
            rowSpacing:0

            MenuOptionBtn {
                id:infoOption
                optionText:i18nd("lliurex-up","Information")
                optionIcon:"/usr/share/icons/breeze/status/22/update-low.svg"
                visible:true
                Connections{
                    function onMenuOptionClicked(){
                        mainStackBridge.manageTransitions(0)
                    }
                }
            }

            MenuOptionBtn {
                id:pkgOption
                optionText:i18nd("lliurex-up","Packages list")
                optionIcon:"/usr/share/icons/breeze/actions/22/view-list-details.svg"
                visible:mainStackBridge.updateRequired
                Connections{
                    function onMenuOptionClicked(){
                        mainStackBridge.manageTransitions(1)
                    }
                }
            }

            MenuOptionBtn {
                id:konsoleOption
                optionText:i18nd("lliurex-up","Update process")
                optionIcon:"/usr/share/icons/breeze/apps/22/utilities-terminal.svg"
                visible:mainStackBridge.enableKonsole
                enabled:true
                Connections{
                    function onMenuOptionClicked(){
                        mainStackBridge.manageTransitions(2)
                    }
                }
            }

            MenuOptionBtn {
                id:settingsOption
                optionText:i18nd("lliurex-up","Settings")
                optionIcon:"/usr/share/icons/breeze/actions/22/configure.svg"
                visible:settingStackBridge.showSettingsPanel
                enabled:true
                Connections{
                    function onMenuOptionClicked(){
                        mainStackBridge.manageTransitions(3)
                    }
                }
            }

            MenuOptionBtn {
                id:helpOption
                optionText:i18nd("lliurex-up","Help")
                optionIcon:"/usr/share/icons/breeze/actions/22/help-contents.svg"
                Connections{
                    function onMenuOptionClicked(){
                        mainStackBridge.openHelp()
                    }
                }
            }
        }
    }

    GridLayout{
        id: layoutGrid
        rows:3 
        flow: GridLayout.TopToBottom
        rowSpacing:0

        StackLayout {
            id: optionsLayout
            currentIndex:mainStackBridge.currentOptionStack
            Layout.fillHeight:true
            Layout.fillWidth:true
            Layout.alignment:Qt.AlignHCenter

            InfoPanel{
                id:infoPanel
            }

            PackagesPanel{
                id:packagesPanel
            }

            KonsolePanel{
                id:konsolePanel
            }

            SettingsPanel{
                id:settingsPanel
            }
           
 
        }

         Kirigami.InlineMessage {
            id: messageLabel
            visible:mainStackBridge.showFeedbackMessage[0]
            text:getResultText()
            type:getMsgType()
            Layout.minimumWidth:555
            Layout.fillWidth:true
            Layout.rightMargin:10
            
        }

        RowLayout{
            id:feedbackRow
            spacing:10
            Layout.topMargin:10
            Layout.bottomMargin:10
            Layout.fillWidth:true

            ColumnLayout{
                id:feedbackColumn
                spacing:10
                Layout.alignment:Qt.AlignHCenter
                Text{
                    id:feedBackText
                    text:{
                        if ((mainStackBridge.updateStep>1)&&(mainStackBridge.updateStep<5)){
                            getFeedBackText()+" "+"( " +mainStackBridge.progressPkg+" "+i18nd("lliurex-up","of")+ " "+infoStackBridge.packagesToUpdate+" )..."
                        }else{
                            getFeedBackText()
                        }
                    }
                    visible:true
                    font.family: "Quattrocento Sans Bold"
                    font.pointSize: 10
                    horizontalAlignment:Text.AlignHCenter
                    Layout.preferredWidth:200
                    Layout.fillWidth:true
                    Layout.alignment:Qt.AlignHCenter
                    wrapMode: Text.WordWrap
                }
                
                ProgressBar{
                    id:feedBackBar
                    from:0.0
                    to:1.0
                    value:mainStackBridge.progressBarValue
                    visible:mainStackBridge.showProgressBar
                    implicitWidth:400
                    Layout.alignment:Qt.AlignHCenter
                }
                
            }
               
            PC3.Button {
                id:updateBtn
                visible:mainStackBridge.showUpdateBtn
                focus:true
                display:AbstractButton.TextBesideIcon
                icon.name:"view-refresh"
                text:i18nd("lliurex-up","Update")
                enabled:mainStackBridge.enableUpdateBtn
                Layout.preferredHeight:40
                Layout.leftMargin:10
                Layout.rightMargin:10
                Keys.onReturnPressed: updateBtn.clicked()
                Keys.onEnterPressed: updateBtn.clicked()
                onClicked:{
                    konsolePanel.runCommand('history -c\n')
                    updateSystem()
                    mainStackBridge.launchUpdateProcess()
                }
                
            }
        }
    }
   
    Timer{
        id:timer
    }

    function delay(delayTime,cb){
        timer.interval=delayTime;
        timer.repeat=true;
        timer.triggered.connect(cb);
        timer.start()
    }
   
    function updateSystem(){
        delay(100, function() {
            if (mainStackBridge.endProcess){
                timer.stop()
                
            }else{
                if (mainStackBridge.endCurrentCommand){
                    mainStackBridge.getNewCommand()
                    var newCommand=mainStackBridge.currentCommand
                    konsolePanel.runCommand(newCommand)
                }
            }
          })
    } 

    function getResultText(){

        var msg=""
        switch(mainStackBridge.showFeedbackMessage[1]){

            case 1:
                msg=i18nd("lliurex-up","The updated process has ended successfully.The system is now update")
                break;
            case 2:
                msg=i18nd("lliurex-up","Your system is update")
                break;
            case -1:
                msg=i18nd("lliurex-up","The updated process has ended with errors")
                break;
        }
        return msg
    }
 
    function getFeedBackText(){

        var msg=""
        var headed=mainStackBridge.updateStep+" "+i18nd("lliurex-up","of")+" "+mainStackBridge.totalUpdateSteps

        switch(mainStackBridge.updateStep){
            case 0:
                msg=""
                return msg
            case 1:
                msg=i18nd("lliurex-up","Preparing system to the update...")
                break;
            case 2:
                msg=i18nd("lliurex-up","Downloading packages")
                break;
            case 3:
                msg=i18nd("lliurex-up","Unpacking packages")
                break;
            case 4:
                msg=i18nd("lliurex-up","Configuring packages")
                break;
            case 5:
                msg=i18nd("lliurex-up","Ending the update...")
                break;
            case 6:
                msg=i18nd("lliurex-up","Checking metapackage...")
                break;
        }
        msg=headed+". "+msg
        return msg
    }

    function getMsgType(){

        switch(mainStackBridge.showFeedbackMessage[2]){
            case "Ok":
                return Kirigami.MessageType.Positive;
            case "Error":
                return Kirigami.MessageType.Error;
            case "Info":
                return Kirigami.MessageType.Information;
            case "Warning":
                return Kirigami.MessageType.Warning;
        }
    }

}

