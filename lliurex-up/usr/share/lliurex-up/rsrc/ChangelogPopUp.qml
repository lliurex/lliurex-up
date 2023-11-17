import org.kde.plasma.core 2.1 as PlasmaCore
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import org.kde.plasma.components 3.0 as PC3

Popup {
    id:changelogPopUp
    width:600
    height:350
    anchors.centerIn: Overlay.overlay
    modal:true
    focus:true
    closePolicy:Popup.AutoClose

    Rectangle{
        id:mainContainer
        width:changelogPopUp.width
        height:changelogPopUp.height
        color:"transparent"
        Text{ 
            id:title
            text:packageStackBridge.pkgChangelog[0]+" "+i18nd("lliurex-up","changelog:")
            font.family: "Quattrocento Sans Bold"
            font.pointSize: 14
        }

        GridLayout{
            id:changelogLayout
            rows:1
            flow: GridLayout.TopToBottom
            rowSpacing:10
            anchors.top:title.bottom
            anchors.topMargin:25
            anchors.left:mainContainer.left
            anchors.horizontalCenter:mainContainer.horizontalCenter
        
            RowLayout{
                Rectangle{
                    id:container
                    color:"transparent"
                    width:580
                    height:230
                    clip:true

                    PC3.ScrollView{
                        implicitWidth:container.width
                        implicitHeight:container.height
                        anchors.leftMargin:11
                        Text{
                            id:pkgChangelogText
                            text:{
                                if (packageStackBridge.pkgChangelog[1]==""){
                                    i18nd("lliurex-up","Searching changelog. Wait a oment...")
                                 }else{
                                     packageStackBridge.pkgChangelog[1]
                                 }
                             } 
                             font.family: "Quattrocento Sans"
                             font.pointSize: 11
                             horizontalAlignment:Text.AlignLeft
                             width:container.width
                             height:container.height
                             wrapMode: Text.WordWrap
                         }
                    }
                }
            }
        }
        RowLayout{
            anchors.bottom:parent.bottom
            anchors.right:parent.right
            anchors.bottomMargin:25
            anchors.rightMargin:25

            PC3.Button {
                id:closeBtn
                visible:true
                focus:true
                display:AbstractButton.TextBesideIcon
                icon.name:"dialog-close"
                text:i18nd("lliurex-up","Close")
                Layout.preferredHeight: 40
                enabled:true
                Keys.onReturnPressed:closeBtn.clicked()
                Keys.onEnterPressed:closeBtn.clicked()
                onClicked:{
                    changelogPopUp.close()
                }
            }
        }
    }
}

