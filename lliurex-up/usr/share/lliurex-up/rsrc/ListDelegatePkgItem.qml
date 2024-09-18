import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQml.Models 2.8
//import org.kde.plasma.components 2.0 as Components
//import org.kde.plasma.components 3.0 as PC3


//Components.ListItem{
ItemDelegate{
    id: listPkgItem
    property string pkgId
    property string pkgVersion
    property string pkgSize
    property string pkgIcon
    property int pkgStatus
    property bool showStatus
  
    enabled:true
    height:60

    /*onContainsMouseChanged: {
        if (containsMouse) {
            listPkg.currentIndex=filterModel.visibleElements.indexOf(index)
        } else {
            listPkg.currentIndex = -1
        }
    }*/

    Item{
       id: menuItem
       height:visible?60:0
       //width:parent.width-15
       width:parent.width-35

       Image {
            id:packageIcon
            source:pkgIcon
            sourceSize.width:35
            sourceSize.height:35
            anchors.left:parent.left
            anchors.verticalCenter:parent.verticalCenter
            anchors.leftMargin:10
            cache:false

        } 
        Column{
            id:pkgDescription
            anchors.verticalCenter:parent.verticalCenter
            anchors.leftMargin:15
            anchors.left:packageIcon.right
            spacing:10
            width:parent.width-(packageSize.width-statusImg.width)

            Text{
                id:pkgName
                text:pkgId
                width: parent.width
                elide:Text.ElideMiddle
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 11
                horizontalAlignment:Text.AlignLeft
            } 
            Text{
                id:packageVersion
                text:pkgVersion
                width: parent.width
                elide:Text.ElideMiddle
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 10
                horizontalAlignment:Text.AlignLeft
            }
        }
        Text{
            id:packageSize
            text:pkgSize
            anchors.verticalCenter:parent.verticalCenter
            anchors.right:{
                if (showStatus){
                    statusImg.left
                }else{
                    if (showChangelogBtn.visible){
                        showChangelogBtn.left
                    }else{
                        parent.right
                    }
                }
            }
            anchors.rightMargin:{
                if (showStatus || showChangelogBtn.visible){
                    15
                }else{
                    10
                }
            }

        }
        Image {
            id: statusImg
            source:{
                if (pkgStatus==0){
                    "/usr/share/lliurex-up/rsrc/ok.png"
                }else{
                    "/usr/share/lliurex-up/rsrc/error.png"
                                 
                }
            }
            visible:showStatus?true:false
            sourceSize.width:32
            sourceSize.height:32
            anchors.leftMargin:10
            anchors.rightMargin:10
            anchors.right:showChangelogBtn.visible?showChangelogBtn.left:parent.right
            anchors.verticalCenter:parent.verticalCenter
        }

        //PC3.Button{
        Button{
            id:showChangelogBtn
            display:AbstractButton.IconOnly
            //icon.name:"help-about"
            icon.source:"/usr/share/icons/breeze/actions/22/help-about"
            anchors.rightMargin:10
            anchors.right:parent.right
            anchors.verticalCenter:parent.verticalCenter
            visible:{
                /*if (listPkgItem.ListView.isCurrentItem){
                    if (mainStackBridge.endProcess){
                        true
                    }else{
                        false
                    }
                }else{
                    false
                }*/
                if (mainStackBridge.endProcess){
                    true
                }else{
                    false
                }
            }
            ToolTip.delay: 1000
            ToolTip.timeout: 3000
            ToolTip.visible: hovered
            //ToolTip.text:i18nd("lliurex-up","Press to view pkg changelog")
            ToolTip.text:"Press to view pkg changelog"
            onClicked:{
                packageStackBridge.showPkgChangelog(pkgId)
                changelogPopUp.open()
            }
        }
     
    }

}
