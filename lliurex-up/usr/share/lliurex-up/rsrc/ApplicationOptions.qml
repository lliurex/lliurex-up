import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

RowLayout{
    id: optionsGrid
    spacing: 10

    Rectangle{
        Layout.preferredWidth: 195
        Layout.fillHeight: true
        border.color: palette.mid

        ColumnLayout{
            id: menuGrid
            Layout.fillWidth:true
            Layout.fillHeight:true
            spacing:0

            MenuOptionBtn {
                id:infoOption
                optionText:i18nd("lliurex-up","Information")
                optionIcon:"update-low"
                visible:true
                Layout.fillWidth:true
                onMenuOptionClicked:mainStackBridge.manageTransitions(0)
            }

            MenuOptionBtn {
                id:pkgOption
                optionText:i18nd("lliurex-up","Packages list")
                optionIcon:"view-list-details"
                visible:mainStackBridge.updateRequired
                Layout.fillWidth:true
                onMenuOptionClicked:mainStackBridge.manageTransitions(1)
            }

            MenuOptionBtn {
                id:konsoleOption
                optionText:i18nd("lliurex-up","Update process")
                optionIcon:"utilities-terminal"
                visible:mainStackBridge.enableKonsole
                Layout.fillWidth:true
                onMenuOptionClicked:mainStackBridge.manageTransitions(2)
            }

            MenuOptionBtn {
                id:settingsOption
                optionText:i18nd("lliurex-up","Settings")
                optionIcon:"configure"
                visible:settingStackBridge.showSettingsPanel
                enabled:mainStackBridge.endProcess
                Layout.fillWidth:true
                onMenuOptionClicked: mainStackBridge.manageTransitions(3)
            }

            MenuOptionBtn {
                id:helpOption
                optionText:i18nd("lliurex-up","Help")
                optionIcon:"help-contents.svg"
                Layout.fillWidth:true
                onMenuOptionClicked: mainStackBridge.openHelp()
           }

            Item {
                Layout.fillHeight:true
            }
        }
    }

    ColumnLayout{
        id: layoutGrid
        Layout.fillWidth: true
        Layout.fillHeight: true
        Layout.leftMargin:5
        Layout.rightMargin:15
        spacing:10

        StackLayout {
            id: optionsLayout
            currentIndex:mainStackBridge.currentOptionStack
            Layout.fillHeight:true
            Layout.fillWidth:true

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
            visible:mainStackBridge.showFeedbackMessage.show
            text:getResultText()
            type:getMsgType()
            Layout.fillWidth:true
      
        }

        RowLayout{
            id:feedbackRow
            spacing:10
            Layout.topMargin:5
            Layout.bottomMargin:15
            Layout.fillWidth:true

            Item {
                Layout.fillWidth: true

            }

            ColumnLayout{
                id:feedbackColumn
                spacing:10
                Layout.alignment:Qt.AlignHCenter
                
                Text{
                    id:feedBackText
                    text:{
                        if (mainStackBridge.updateStep>1 && mainStackBridge.updateStep<5){
                            getFeedBackText()+" "+"( " +mainStackBridge.progressPkg+" "+i18nd("lliurex-up","of")+ " "+infoStackBridge.packagesInfo.totalPackages+" )..."
                        }else{
                            getFeedBackText()
                        }
                    }
                    visible:true
                    font.pointSize: 10
                    horizontalAlignment:Text.AlignHCenter
                    Layout.maximumWidth: 500
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

            Item {
                Layout.fillWidth: true

            }
               
            Button {
                id: updateBtn
                visible: mainStackBridge.showUpdateBtn && mainStackBridge.currentOptionStack !== 3
                focus: visible
                display: AbstractButton.TextBesideIcon
                icon.name: "view-refresh"
                text: i18nd("lliurex-up","Update")
                enabled :mainStackBridge.enableUpdateBtn
                Layout.leftMargin: 10
                Layout.rightMargin: 10
                Layout.alignment:Qt.AlignRight | Qt.AlignVCenter
                Keys.onReturnPressed: updateBtn.clicked()
                Keys.onEnterPressed: updateBtn.clicked()
                onClicked:{
                    konsolePanel.runCommand('history -c\n')
                    updateSystem()
                    mainStackBridge.launchUpdateProcess()
                }
                
            }

            Button {
                id:applyBtn
                visible: mainStackBridge.currentOptionStack === 3
                focus:visible
                display:AbstractButton.TextBesideIcon
                icon.name:"dialog-ok"
                text:i18nd("lliurex-up","Apply")
                enabled:settingStackBridge.changesInSettings
                Layout.leftMargin:10
                Layout.rightMargin:10
                Layout.alignment:Qt.AlignRight | Qt.AlignVCenter
                Keys.onReturnPressed: applyBtn.clicked()
                Keys.onEnterPressed: applyBtn.clicked()
                onClicked:settingStackBridge.applyChanges()
            }
            
            Button {
                id:cancelBtn
                visible: mainStackBridge.currentOptionStack === 3
                focus: false
                display:AbstractButton.TextBesideIcon
                icon.name:"dialog-cancel"
                text:i18nd("lliurex-up","Cancel")
                enabled:settingStackBridge.changesInSettings
                Layout.leftMargin:10
                Layout.rightMargin:10
                Layout.alignment:Qt.AlignRight | Qt.AlignVCenter
                Keys.onReturnPressed: cancelBtn.clicked()
                Keys.onEnterPressed: cancelBtn.clicked()
                onClicked:settingStackBridge.discardChanges()
            }
        }
    }

    ChangesDialog{

        id:pendingChangesDialog
        dialogVisible:mainStackBridge.showPendingChangesDialog
        
        Connections{
            target:pendingChangesDialog
            function onDialogApplyClicked(){
               mainStackBridge.managePendingChangesDialog("Apply")
            }
            function onDiscardDialogClicked(){
               mainStackBridge.managePendingChangesDialog("Discard")
            }
            function onRejectDialogClicked(){
                mainStackBridge.managePendingChangesDialog("Cancel")
            }
        }
    }
    
    CustomPopup{
        id:waitPopup
    }

    Timer{
        id:timer
        interval:100
        repeat:true
        onTriggered:{
            if (mainStackBridge.endProcess){
                timer.stop()
            }else{
                if (mainStackBridge.endCurrentCommand){
                    mainStackBridge.getNewCommand()
                    var newCommand=mainStackBridge.currentCommand
                    konsolePanel.runCommand(newCommand)
                }  
            }
        }
    }
   
    function updateSystem(){
        timer.restart()
    } 

    function getResultText(){

        switch(mainStackBridge.showFeedbackMessage.msgCode){

            case 1:
                return i18nd("lliurex-up","The updated process has ended successfully.The system is now update")
            case 2:
                return i18nd("lliurex-up","Your system is update")
            case -1:
                return i18nd("lliurex-up","The updated process has ended with errors")
            case -8:
                return i18nd("lliurex-up","dpkg --configure -a must be executed. You can use dpkg-unlocker for this")
            default:
                return ""
        }
    }
 
    function getFeedBackText(){

        let headed = mainStackBridge.updateStep+" "+i18nd("lliurex-up","of")+" "+mainStackBridge.totalUpdateSteps
        let msg

        switch(mainStackBridge.updateStep){
            case 0:
            default:
                return ""
            case 1:
                msg = i18nd("lliurex-up","Preparing system to the update...")
                break;
            case 2:
                msg = i18nd("lliurex-up","Downloading packages")
                break;
            case 3:
                msg = i18nd("lliurex-up","Unpacking packages")
                break;
            case 4:
                msg = i18nd("lliurex-up","Configuring packages")
                break;
            case 5:
                msg = i18nd("lliurex-up","Ending the update...")
                break;
            case 6:
                msg = i18nd("lliurex-up","Checking metapackage...")
                break;
            case 7:
                msg = i18nd("lliurex-up","Updating Flatpak applications...")
                break;
        }
        return headed + ". " + msg
     }

    function getMsgType(){

        switch(mainStackBridge.showFeedbackMessage.type){
            case 0:
                return Kirigami.MessageType.Positive
            case 1:
                return Kirigami.MessageType.Error
            case 2:
                return Kirigami.MessageType.Warning;
            case 3:
            default:
                return Kirigami.MessageType.Information
         }
    }
}

