import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.plasma.components as PC

Popup {
    id:changelogPopUp
    width:600
    height:350
    anchors.centerIn: Overlay.overlay
    modal:true
    focus:true
    closePolicy:Popup.AutoClose
    background:Rectangle{
        color:"#ebeced"
        border.color:"#b8b9ba"
        border.width:1
        radius:5.0
    }

    contentItem:Rectangle{
        id:mainContainer
        width:changelogPopUp.width
        height:changelogPopUp.height
        color:"transparent"
        Text{
            id:changelogText
            text:i18nd("lliurex-up","Changelog")
            font.family: "Quattrocento Sans Bold"
            font.pointSize: 16
            anchors.top:changelogPopUp.bottom
        }

        GridLayout{
            id:changelogLayout
            rows:1
            flow: GridLayout.TopToBottom
            rowSpacing:10
            anchors.top:changelogText.bottom
            anchors.topMargin:25
            anchors.leftMargin:10
            anchors.left:mainContainer.left
            anchors.horizontalCenter:mainContainer.horizontalCenter
        
            RowLayout{
                Rectangle{
                    id:container
                    color:"transparent"
                    width:565
                    height:215
                    clip:true

                    PC.ScrollView{
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
                             horizontalAlignment:{
                              if (packageStackBridge.pkgChangelog[1]==""){
                                    Text.AlignHCenter
                                }else{
                                    Text.AlignLeft
                                }
                             }
                             verticalAlignment:{
                                if (packageStackBridge.pkgChangelog[1]==""){
                                    Text.AlignVCenter
                                }else{
                                    Text.AlignTop
                                }
                             }
                             width:container.width-10
                             height:container.height-10
                             wrapMode: Text.WordWrap
                         }
                    }
                }
            }
        }
        RowLayout{
            anchors.bottom:parent.bottom
            anchors.right:parent.right
            anchors.bottomMargin:10
            anchors.rightMargin:10

            PC.Button {
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

