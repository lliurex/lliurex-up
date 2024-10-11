import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.kirigami 2.16 as Kirigami


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
     			text:i18nd("lliurex-up","Show notifications for available updates:")
				font.family: "Quattrocento Sans Bold"
				font.pointSize: 10
				Layout.alignment:Qt.AlignRight
				Layout.bottomMargin:10
			}   

			Switch {
				id:notificationToggleswitch
				checked: settingStackBridge.isSystrayEnabled
				Layout.alignment:Qt.AlignLeft
				Layout.bottomMargin:10
				indicator: Rectangle {
					implicitWidth: 40
					implicitHeight: 10
					x: notificationToggleswitch.width - width - notificationToggleswitch.rightPadding
					y: parent.height/2 - height/2 
					radius: 7
					color: notificationToggleswitch.checked ? "#3daee9" : "#d3d3d3"

					Rectangle {
						x: notificationToggleswitch.checked ? parent.width - width : 0
						width: 20
						height: 20
						y:parent.height/2-height/2
						radius: 10
						border.color: "#808080"
				   }
				}
				onToggled: {
					settingStackBridge.manageSystray(notificationToggleswitch.checked);
				}
			}

			Text {
     			id:textAutoUpgradeSettings
     			text:i18nd("lliurex-up","Activate automatic system update:")
				font.family: "Quattrocento Sans Bold"
				font.pointSize: 10
				visible:settingStackBridge.isAutoUpgradeAvailable
				Layout.alignment:Qt.AlignRight
			}   

			Switch {
				id:autoUpgradeToggleswitch
				checked:settingStackBridge.isAutoUpgradeEnabled
				enabled:!settingStackBridge.isAutoUpgradeRun
				visible:settingStackBridge.isAutoUpgradeAvailable
				Layout.alignment:Qt.AlignLeft
				indicator: Rectangle {
					implicitWidth: 40
					implicitHeight: 10
					x: autoUpgradeToggleswitch.width - width - autoUpgradeToggleswitch.rightPadding
					y: parent.height/2 - height/2 
					radius: 7
					color: autoUpgradeToggleswitch.checked ? "#3daee9" : "#d3d3d3"

					Rectangle {
						x: autoUpgradeToggleswitch.checked ? parent.width - width : 0
						width: 20
						height: 20
						y:parent.height/2-height/2
						radius: 10
						border.color: "#808080"
				   }
				}	
				hoverEnabled:true
				ToolTip.delay: 1000
				ToolTip.timeout: 3000
				ToolTip.visible: hovered
				ToolTip.text:i18nd("lliurex-up","If it is activated the system will update automatically at login")

				onToggled: {
					settingStackBridge.manageAutoUpgrade(autoUpgradeToggleswitch.checked);
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
