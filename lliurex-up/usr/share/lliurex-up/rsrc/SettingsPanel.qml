import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.kirigami 2.16 as Kirigami
import org.kde.plasma.components as PC


Rectangle{
    color:"transparent"
    enabled:{
    	if (settingStackBridge.isAutoUpgradeRun){
    		false
    	}else{
    	  	if (mainStackBridge.endProcess){
    	  		true
    	  	}else{
    	  		false
    	  	}
    	}
    }
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
     		Layout.topMargin:messageLabel.visible?5:50

     		Text {
     			id:textNotificationSettings
     			text:i18nd("lliurex-up","Notifications:")
				font.family: "Quattrocento Sans Bold"
				font.pointSize: 10
				Layout.alignment:Qt.AlignRight
				Layout.bottomMargin:10
			}   

			PC.CheckBox {
				id:notificationCB
				checked: settingStackBridge.isSystrayEnabled
				text:i18nd("lliurex-up","Show notifications for available updates")
				enabled:true
				font.family: "Quattrocento Sans Bold"
				font.pointSize: 10
				focusPolicy: Qt.NoFocus
				onToggled:settingStackBridge.manageSystray(notificationCB.checked);
				Layout.bottomMargin:10
				Layout.alignment:Qt.AlignLeft
			}

			Text {
     			id:textAutoUpgradeSettings
     			text:i18nd("lliurex-up","Updates:")
				font.family: "Quattrocento Sans Bold"
				font.pointSize: 10
				visible:{
					if (settingStackBridge.isAutoUpgradeAvailable && settingStackBridge.isAdmin){
						true
					}else{
						false
					}
				}
				Layout.bottomMargin:10
				Layout.alignment:Qt.AlignRight
			} 

			PC.CheckBox {
				id:autoUpgradeCB
				checked: settingStackBridge.isAutoUpgradeEnabled
				text:i18nd("lliurex-up","Activate automatic system updates")
				enabled:true
				visible:{
					if (settingStackBridge.isAutoUpgradeAvailable && settingStackBridge.isAdmin){
						true
					}else{
						false
					}
				}
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

				PC.CheckBox {
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
						settingStackBridge.manageUpdatePause(checked)
					}
				} 
				ComboBox{
					id:pauseValues
					currentIndex:settingStackBridge.weeksOfPause
					textRole:"name"
					model:settingStackBridge.weeksOfPauseCombo
					enabled:{
						if (settingStackBridge.isWeekPauseActive && settingStackBridge.canEditWeekPause){
							true
						}else{
							false
						}
					}
					Layout.alignment:Qt.AlignVCenter
					Layout.bottomMargin:10
					Layout.preferredWidth:100
					onActivated:{
						settingStackBridge.manageWeeksOfPause(pauseValues.currentIndex)
					}
				}
				PC.Button {
					id:extensionPauseBtn
					display:AbstractButton.IconOnly
					icon.name:"document-edit"
					ToolTip {
						id:extensionPauseToolTip
						delay: 1000
						timeout: 3000
						visible: extensionPauseBtn.hovered
						text:i18nd("lliurex-up","Click to extend the pause of automatic updates")
						background:Rectangle{
							color:"#ffffff"
							border.color:"#b8b9ba"
							radius:5.0
						}
					}
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
						settingStackBridge.manageExtensionPauseBtn(extensionRow.visible)
					}
				}
			}

			Text{
				id:extensionText
				visible:settingStackBridge.showExtensionPauseCombo
			}

			RowLayout{
				id:extensionRow
				visible:settingStackBridge.showExtensionPauseCombo

				Text{
					id:textExtensionPause
					text:i18nd("lliurex-up","Extended pause for:")
					font.family: "Quattrocento Sans Bold"
					font.pointSize: 10
					Layout.bottomMargin:10
					Layout.alignment:Qt.AlignRight
				} 

				ComboBox{
					id:extensionValues
					currentIndex:settingStackBridge.extensionWeekPause
					textRole:"name"
					model:settingStackBridge.extensionPauseCombo
					Layout.alignment:Qt.AlignVCenter
					Layout.bottomMargin:10
					Layout.preferredWidth:150
					onActivated:{
						settingStackBridge.manageExtensionPause(extensionValues.currentIndex)
					}
				}
			}
		}

	}

	 
   function getMsg(){

		var msg=""
		switch(settingStackBridge.showSettingsMsg[1]){
			case -1:
				msg=i18nd("lliurex-up","It is not possible to change notifications setting")
				break;
			case -2:
				msg=i18nd("lliurex-up","It is not possible to change automatic updates setting")
				break;
			case -3:
				msg=i18nd("lliurex-up","It is not possible to change automatic updates pause setting")
				break;
			case -4:
				msg=i18nd("lliurex-up","It is not posible to change settings")
				break;
			case 0:
				msg=i18nd("lliurex-up","Changes will take effect the next time the computer turns on or restarts")
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
