import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import org.kde.kirigami 2.16 as Kirigami


Rectangle{
    color:"transparent"
    Text{ 
       text:i18nd("lliurex-up","System settings")
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
            visible:settingStackBridge.showSettingsMsg
            text:i18nd("lliurex-up","Changes will take effect the next time you log in")
            type:Kirigami.MessageType.Positive
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
     			id:textMessageSettings
     			text:i18nd("lliurex-up","Show notifications for available updates:")
				font.family: "Quattrocento Sans Bold"
				font.pointSize: 10
				Layout.alignment:Qt.AlignRight
			}   

			Switch {
				id:toggleswitch
				checked: settingStackBridge.isSystrayEnabled
				Layout.alignment:Qt.AlignLeft
				indicator: Rectangle {
					implicitWidth: 40
					implicitHeight: 10
					x: toggleswitch.width - width - toggleswitch.rightPadding
					y: parent.height/2 - height/2 
					radius: 7
					color: toggleswitch.checked ? "#3daee9" : "#d3d3d3"

					Rectangle {
						x: toggleswitch.checked ? parent.width - width : 0
						width: 20
						height: 20
						y:parent.height/2-height/2
						radius: 10
						border.color: "#808080"
				   }
				}	

				onToggled: {
					settingStackBridge.manageSystray(toggleswitch.checked);
				}
			}
		}

	}
}