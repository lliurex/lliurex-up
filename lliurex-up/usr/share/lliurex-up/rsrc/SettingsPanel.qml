import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import org.kde.kirigami 2.16 as Kirigami
import org.kde.plasma.components 3.0 as PC3


Rectangle{
    color:"transparent"
    Text{ 
       text:i18nd("lliurex-up","Settings")
        font.family: "Quattrocento Sans Bold"
        font.pointSize: 16
    }

    GridLayout {
    	id: mainGridSettings
		rows:2
		flow: GridLayout.TopToBottom
		width:parent.width-10
		anchors.horizontalCenter:parent.horizontalCenter
		
		Kirigami.InlineMessage {
            id: messageLabel
            visible:settingStackBridge.showSettingsMsg[0]
            text:getMsg()
            type:getMsgType()
            Layout.minimumWidth:580
            Layout.fillWidth:true
            Layout.topMargin: 40
      }
		       
     	GridLayout {
     		id: settingsGrid
     		columns:2
     		flow: GridLayout.LeftToRight
     		Layout.bottomMargin: 10
     		columnSpacing:10
     		Layout.alignment:Qt.AlignHCenter
     		Layout.topMargin:messageLabel.visible?0:55

     		Text {
     			id:textNotificationSettings
     			text:i18nd("lliurex-up","Notifications:")
				font.family: "Quattrocento Sans Bold"
				font.pointSize: 10
				Layout.alignment:Qt.AlignRight
				Layout.bottomMargin:10
			}   

			PC3.CheckBox {
				id:notificationCB
				checked: settingStackBridge.isSystrayEnabled
				text:i18nd("lliurex-up","Show notifications for available updates")
				enabled:true
				font.family: "Quattrocento Sans Bold"
				font.pointSize: 10
				focusPolicy: Qt.NoFocus
				onToggled:settingsStackBridge.manageAutoStart(autoStartValue.checked);
				Layout.bottomMargin:10
				Layout.alignment:Qt.AlignLeft
			}

			Text {
     			id:textAutoUpgradeSettings
     			text:i18nd("lliurex-up","Updates:")
				font.family: "Quattrocento Sans Bold"
				font.pointSize: 10
				visible:true
				Layout.bottomMargin:10
				Layout.alignment:Qt.AlignRight
			} 

			PC3.CheckBox {
				id:autoUpgradeCB
				checked: settingStackBridge.isAutoUpgradeEnabled
				text:i18nd("lliurex-up","Activate automatic system updates")
				enabled:true
				visible:true
				font.family: "Quattrocento Sans Bold"
				font.pointSize: 10
				focusPolicy: Qt.NoFocus
            			Layout.bottomMargin:10
            			Layout.alignment:Qt.AlignLeft
			    	onToggled:{
			    		settingStackBridge.manageAutoUpgrade(checked)
			    	}
			}  

			Text {
     			id:textPauseAutoSettings
     			text:i18nd("lliurex-up","Pause updates:")
				font.family: "Quattrocento Sans Bold"
				font.pointSize: 10
				visible:settingStackBridge.isAutoUpgradeEnabled
				Layout.bottomMargin:10
				Layout.alignment:Qt.AlignRight
			} 
			RowLayout{
				id:pauseRow
				visible:settingStackBridge.isAutoUpgradeEnabled

				PC3.CheckBox {
					id:pauseUpgradeCB
					checked: settingStackBridge.isWeekPauseActive
					text:i18nd("lliurex-up","Pause automatic updates for: ")
					enabled:{
						if (!mainStackBridge.updateRequired){
							true
						}else{
							settingStackBridge.canPauseUpdate
						}
					}
					font.family: "Quattrocento Sans Bold"
					font.pointSize: 10
					focusPolicy: Qt.NoFocus
	            			Layout.bottomMargin:10
	           	 		Layout.alignment:Qt.AlignLeft
	            			onToggled:{
               					if (checked && settingStackBridge.canPauseUpdate){
               						pauseValues.enabled=true
               					}else{
               						pauseValues.enabled=false
               					}
               				}

				} 
				PC3.ComboBox{
				       id:pauseValues
				       currentIndex:settingStackBridge.weeksOfPause
				       textRole:"name"
				       model:settingStackBridge.weeksOfPauseCombo
				       enabled:false
				       Layout.alignment:Qt.AlignVCenter
				       Layout.bottomMargin:10
				       Layout.preferredWidth:100
            			}

            
            PC3.Button {
               id:extendedPauseBtn
               display:AbstractButton.IconOnly
               icon.name:"document-edit"
               ToolTip.delay: 1000
               ToolTip.timeout: 3000
               ToolTip.visible: hovered
               ToolTip.text:i18nd("lliurex-up","Click to extend the pause of automatic updates")
               hoverEnabled:true
               enabled:{
               	if (pauseUpgradeCB.checked && settingStackBridge.canExtendedPause){
               		true
               	}else{
               		false
               	}
               }
               Layout.preferredHeight: 35
               Layout.alignment:Qt.AlignVCenter
               Layout.bottomMargin:10
               onClicked:{
               	extensionText.visible=!extensionText.visible
               	extensionRow.visible=!extensionRow.visible
               }
            }
            
         }
         Text{
         	id:extensionText
         	visible:false

         }
         RowLayout{
         	id:extensionRow
         	visible:false

         	Text {
	     		id:textExtendedPause
	     		text:i18nd("lliurex-up","Extended pause for:")
			font.family: "Quattrocento Sans Bold"
			font.pointSize: 10
			Layout.bottomMargin:10
			Layout.alignment:Qt.AlignRight
		} 

		PC3.ComboBox{
		       id:extendedValues
		       currentIndex:0
		       textRole:"name"

		       model:settingStackBridge.extensionPauseCombo
		       Layout.alignment:Qt.AlignVCenter
		       Layout.bottomMargin:10
		       Layout.preferredWidth:130
		}

         }

			
		}

	}

	
   
   function getMsg(){

		var msg=""
		switch(settingStackBridge.showSettingsMsg[1]){
			case -1:
				msg=i18nd("lliurex-up","Unable to activate the automatic system update")
				break;
			case -2:
				msg=i18nd("lliurex-up","Unable to deactivate automatic system update")
				break;
			case 0:
				msg=i18nd("lliurex-up","Changes will take effect the next time you log in")
				break;
			case 1:
				msg=i18nd("lliurex-up","Changes will take effect the next time the computer turns on or restarts")
				break;
			case 2:
				msg=i18nd("lliurex-up","Automatic system update has been successfully disabled")
				break;
         }
        return msg
	}

	function getMsgType(){

		switch(settingStackBridge.showSettingsMsg[2]){
			case "Ok":
				return Kirigami.MessageType.Positive;
			case "Error":
				return Kirigami.MessageType.Error;
		}	
	}
}
