import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
//import org.kde.plasma.components 3.0 as PC3

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
    }

    contentItem:Rectangle{
        id:mainContainer
        width:changelogPopUp.width
        height:changelogPopUp.height
        color:"transparent"
        Text{ 
            id:changelogText
            //text:i18nd("lliurex-up","Changelog")
            text:"Changelog"
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
            anchors.left:mainContainer.left
            anchors.horizontalCenter:mainContainer.horizontalCenter
        
            RowLayout{
                Rectangle{
                    id:container
                    color:"transparent"
                    width:575
                    height:215
                    clip:true

                    //PC3.ScrollView{
                    ScrollView{
                        implicitWidth:container.width
                        implicitHeight:container.height
                        anchors.leftMargin:11
                        Text{
                            id:pkgChangelogText
                            text:{
                                if (packageStackBridge.pkgChangelog[1]==""){
                                    //i18nd("lliurex-up","Searching changelog. Wait a oment...")
                                    "Searching changelog. Wait a oment..."
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

            //PC3.Button {
            Button{
                id:closeBtn
                visible:true
                focus:true
                display:AbstractButton.TextBesideIcon
                //icon.name:"dialog-close"
                icon.source:"/usr/share/icons/breeze/actions/22/dialog-close.svg"
                //text:i18nd("lliurex-up","Close")
                text:"Close"
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

