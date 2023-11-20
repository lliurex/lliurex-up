import org.kde.plasma.core 2.1 as PlasmaCore
import org.kde.plasma.components 3.0 as PC3
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15

ApplicationWindow {
	id:window
	visible: true
	title: "LliureX-Up"
	property int margin: 1
	color:"#eff0f1"
	width: 610
	height: mainLayout.implicitHeight + 2 * margin
	minimumWidth: 610
	minimumHeight: mainLayout.Layout.minimumHeight + 2 * margin
	maximumWidth: 610
	maximumHeight: mainLayout.Layout.maximumHeight + 2 * margin
	Component.onCompleted: {
	    x = Screen.width/2 - width/2 
        y = Screen.height/2 - height/2

    }

    onClosing: {
     	if (launchStackBridge.closed(true))
     		close.accepted=true;
        else
        	close.accepted=false;	
              
    }

    ColumnLayout {
    	id: mainLayout
    	anchors.fill: parent
    	anchors.margins: margin
    	Layout.minimumWidth:610	
    	Layout.maximumWidth:610
    	Layout.minimumHeight:170
    	Layout.maximumHeight:170
    	
	   	GridLayout {
	   		id: grid
	   		Layout.topMargin: 5
	   		Layout.bottomMargin: 0
	   		rows: 3
	   		columns: 2
	   		Rectangle {
	   			color:"transparent"
	   			Layout.rowSpan: 1
	   			Layout.columnSpan: 1
	   			Layout.leftMargin:10
	   			width:60
	   			height:60
	   			Image{
	   				source:"/usr/share/icons/breeze/status/64/dialog-warning.svg"
	   				anchors.centerIn:parent
	   			}
	   		}
	   		Rectangle {
	   			color:"transparent"
	   			Layout.rowSpan: 1
	   			Layout.columnSpan: 1
	   			height:60
	   			Layout.fillWidth: true
	   			Layout.leftMargin:10
	   			Text{
	   				id:warningText
	   				text:getText()
	   				font.family: "Quattrocento Sans Bold"
	   				font.pointSize: 11
	   				anchors.left: parent.left
	   				anchors.verticalCenter:parent.verticalCenter
	   			}
	   		}
	   		Rectangle {
	   			color:"transparent"
	   			Layout.rowSpan: 1
	   			Layout.columnSpan: 2
	   			Layout.fillWidth: true
	   			height:20
                ProgressBar{
                    id:feedBackBar
                    indeterminate:true
                    visible:launchStackBridge.isProgressBarVisible
                    implicitWidth:250
                    anchors.centerIn:parent
                }
	   		}
	   		Rectangle {
	   			id:btnBox
	   			color:"transparent"
	   			visible:!feedBackBar.visible
	   			Layout.rowSpan: 1
	   			Layout.columnSpan: 2
	   			Layout.fillWidth: true
	   			Layout.rightMargin:10
	   			height:60

	   			PC3.Button{
	   				id:applyBtn
	   				height: 40
	   				anchors.right: cancelBtn.left
	   				anchors.rightMargin:15
	   				anchors.verticalCenter:parent.verticalCenter
	   				display:AbstractButton.TextBesideIcon
	   				icon.name:"dialog-ok"
	   				text:i18nd("lliurex-up","Yes")
	   				visible:launchStackBridge.showApplyBtn
	   				Keys.onReturnPressed: applyBtn.clicked()
	                Keys.onEnterPressed: applyBtn.clicked()
	                onClicked:{
	                   launchStackBridge.launchUnlockProcess()
	                } 
				}	
	   			PC3.Button {
	   				id:cancelBtn
	   				height: 40
	   				anchors.right: parent.right
	   				anchors.verticalCenter:parent.verticalCenter
	   				display:AbstractButton.TextBesideIcon
	   				icon.name:launchStackBridge.showApplyBtn?"dialog-cancel":"dialog-close"
	   				text:launchStackBridge.showApplyBtn?i18nd("lliurex-up","No"):i18nd("lliurex-up","Close")
	   				Keys.onReturnPressed: cancelBtn.clicked()
	                Keys.onEnterPressed: cancelBtn.clicked()
	                onClicked:{
	                   window.close()
	                } 
				}	
		    }
		}
	
	 }

	 function getText(){

	 	var msg=""
	 	switch(launchStackBridge.dialogTextCode){
	 		case 1:
	 			msg=launchStackBridge.lockedService+" "+i18nd("lliurex-up","is now running. Wait a moment and try again")
	 			break;
	 		case 2:
	 			msg=i18nd("lliurex-up","Some process are running. Wait a moment and try again")
	 			break;
	 		case 3:
	 			msg=launchStackBridge.lockedService+" "+i18nd("lliurex-up","seems blocked by a failed previous execution.\nLliurex-Up can not continue if this block is maintained.\nDo you want to try to unlock it?")
	 			break; 
	 		case 4:
	 			msg=i18nd("lliurex-up","The unlocking process is running. Wait a moment...")
	 			break;
	 		case -1:
	 			msg=i18nd("lliurex-up","You need administration privileges to run this application.")
	 			break;
	 		case -2:
	 			msg=i18nd("lliurex-up","The unlocking process has failed")
	 			break;
	 	}
	 	return msg;
	 }
}  		
