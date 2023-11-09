import org.kde.plasma.core 2.1 as PlasmaCore
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15

ApplicationWindow {

    property bool closing: false
    id:mainWindow
    visible: true
    title: "LliureX-Up"
    color:"#eff0f1"
    property int margin: 1
    width: mainLayout.implicitWidth + 2 * margin
    height: mainLayout.implicitHeight + 2 * margin
    minimumWidth: mainLayout.Layout.minimumWidth + 2 * margin
    minimumHeight: mainLayout.Layout.minimumHeight + 2 * margin
    Component.onCompleted: {
        x = Screen.width / 2 - width / 2
        y = Screen.height / 2 - height / 2
    }
    onClosing: {
        close.accepted=closing;
        mainStackBridge.closeApplication()
        delay(100, function() {
            if (mainStackBridge.closeGui){
                closing=true,
                closeTimer.stop(), 
                mainWindow.close();
            }
        })
        
    }
    
    ColumnLayout {
        id: mainLayout
        anchors.fill: parent
        anchors.margins: margin
        Layout.minimumWidth:800
        Layout.preferredWidth:800
        Layout.minimumHeight:580

        RowLayout {
            id: bannerBox
            Layout.alignment:Qt.AlignTop
            
            Rectangle{
                color: "#000886"
                Layout.minimumWidth:mainLayout.width
                Layout.preferredWidth:mainLayout.width
                Layout.fillWidth:true
                Layout.minimumHeight:120
                Layout.maximumHeight:120
                Image{
                    id:banner
                    source: "/usr/share/lliurex-up/rsrc/lliurex-up-banner.png"
                    anchors.centerIn:parent
                }
            }
        }

        StackView {
            id: mainView
            property int currentView:mainStackBridge.currentStack
            Layout.minimumWidth:800
            Layout.preferredWidth: 800
            Layout.minimumHeight:460
            Layout.preferredHeight:460
            Layout.alignment:Qt.AlignHCenter|Qt.AlignVCenter
            Layout.leftMargin:0
            Layout.fillWidth:true
            Layout.fillHeight: true

            initialItem:loadView

            onCurrentViewChanged:{
                switch(currentView){
                    case 0:
                        mainView.replace(loadView)
                        break;
                    case 1:
                        mainView.replace(errorView)
                        break;
                    case 2:
                        mainView.replace(applicationOptionsView)
                        break;
                }
            }
       }
       
       Component{
            id:loadView
            LoadPanel{
                id:loadPanel
            }
       } 
       Component{
            id:errorView
            ErrorPanel{
                id:errorPanel
            }
        }
        Component{
            id:applicationOptionsView
            ApplicationOptions{
                id:applicationOptions
            }
        }
      
    }

    Timer{
        id:closeTimer
    }

    function delay(delayTime,cb){
        closeTimer.interval=delayTime;
        closeTimer.repeat=true;
        closeTimer.triggered.connect(cb);
        closeTimer.start()
    }

}

