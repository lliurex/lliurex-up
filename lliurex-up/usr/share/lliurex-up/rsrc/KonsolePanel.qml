import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QMLTermWidget

Rectangle{
    color:"transparent"

    ColumnLayout{
        id: mainContent
        anchors.fill: parent
        anchors.leftMargin: 5
        anchors.rightMargin: 15
        anchors.bottomMargin: 15
        spacing: 10

        Text{ 
            text: i18nd("lliurex-up","Update process")
            font.pointSize: 16
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            
            QMLTermWidget {
                id: terminal
                anchors.fill: parent
                font.family: "Monospace"
                font.pointSize: 9
                colorScheme: "cool-retro-term"
                session: QMLTermSession{
                    id: mainsession
                    initialWorkingDirectory: "$HOME"
                }
                Component.onCompleted: {
                    mainsession.startShellProgram();
                    mainsession.sendText('setterm -cursor off;stty -echo;PS1="";history -c;clear;\n');
                }

            }

            QMLTermScrollbar {
                terminal: terminal
                width: 20
                Rectangle {
                    opacity: 0.8
                    anchors.margins: 5
                    radius: width * 0.5
                    anchors.fill: parent
                }
            }
        
        }
    }
    
    function runCommand(command){
        mainsession.sendText('\n')
        mainsession.sendText(command)

    } 

} 
