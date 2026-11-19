import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami
import org.kde.plasma.components as PC


Rectangle{
	id:rectLayout
    	color:"transparent"

	ColumnLayout{
        id:generalLayout
        anchors.fill: parent
        anchors.leftMargin:5
        anchors.bottomMargin:15
        spacing: 10


	    Text{ 
	        text:i18nd("lliurex-up","Settings")
	        font.pointSize: 16
	    }

	    Kirigami.InlineMessage {
            id: messageLabel
            visible:settingStackBridge.showSettingsMsg.show
            text:getMsg()
            type:getMsgType()
            Layout.fillWidth:true
      	}

	    GridLayout{
            id: infoLayout
            columns: 2
            rowSpacing: 10
            Layout.topMargin: 5
            Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter

            Text {
     			id:textNotificationSettings
     			text:i18nd("lliurex-up","Notifications:")
				font.pointSize: 10
				Layout.alignment:Qt.AlignRight | Qt.AlignVCenter
			}   

	        CheckBox {
                id:notificationCB
                text:i18nd("lliurex-up","Show notifications for available updates")
                checked: settingStackBridge.isSystrayEnabled
                font.pointSize: 10
                focusPolicy: Qt.NoFocus
                Keys.onReturnPressed: enableWifiCb.toggled()
                Keys.onEnterPressed: enableWifiCb.toggled()
                onToggled:settingStackBridge.manageSystray(notificationCB.checked);
                Layout.alignment:Qt.AlignLeft | Qt.AlignVCenter
            }
        }

        Item {
            Layout.fillHeight: true
        }
    }
	 
   function getMsg(){

		switch(settingStackBridge.showSettingsMsg.msgCode){
			case -1:
				return i18nd("lliurex-up","It is not possible to change notifications setting")
			case 0:
				return i18nd("lliurex-up","Changes will take effect the next time the computer turns on or restarts")
			default:
				return ""
		}
	}

	function getMsgType(){

		switch(settingStackBridge.showSettingsMsg.type){
			case 0:
				return Kirigami.MessageType.Positive
			case 1:
				return Kirigami.MessageType.Error
			case 2:
				return Kirigami.MessageType.Warning
			case 3:
			default:
				return Kirigami.MessageType.Information
		}	
	}
}
