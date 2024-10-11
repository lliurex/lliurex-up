import QtQuick
import QtQuick.Controls
import QtQml.Models
import org.kde.plasma.components as PC
import org.kde.kirigami as Kirigami
import QtQuick.Layouts


Rectangle{
    property alias packagesModel:filterModel.model
    property alias listCount:listPkg.count
    id: optionsGrid
    color:"transparent"

    GridLayout{
        id:mainGrid
        rows:2
        flow: GridLayout.TopToBottom
        rowSpacing:10
        anchors.left:parent.left
        anchors.fill:parent

        PC.TextField{
            id:pkgSearchEntry
            font.pointSize:10
            horizontalAlignment:TextInput.AlignLeft
            Layout.alignment:Qt.AlignRight
            Layout.topMargin:40
            focus:true
            width:100
            placeholderText:i18nd("lliurex-up","Search...")
            onTextChanged:{
                filterModel.update()
            }
        }

        Rectangle {
            id:pkgTable
            visible: true
            color:"white"
            Layout.fillHeight:true
            Layout.fillWidth:true
            Layout.topMargin:10
     
            border.color: "#d3d3d3"

            PC.ScrollView{
                implicitWidth:parent.width
                implicitHeight:parent.height
                anchors.leftMargin:10
       
                ListView{
                    id: listPkg
                    property int totalItems
                    anchors.fill:parent
                    height: parent.height
                    enabled:true
                    currentIndex:-1
                    clip: true
                    focus:true
                    boundsBehavior: Flickable.StopAtBounds
                    highlight: Rectangle { color: "#add8e6"; opacity:0.8;border.color:"#53a1c9" }
                    highlightMoveDuration: 0
                    highlightResizeDuration: 0
                    model:FilterDelegateModel{
                        id:filterModel
                        model:packagesModel
                        role:"pkgId"
                        search:pkgSearchEntry.text.trim()
                        
                        delegate: ListDelegatePkgItem{
                            width:pkgTable.width
                            pkgId:model.pkgId
                            pkgVersion:model.pkgVersion
                            pkgSize:model.pkgSize
                            pkgIcon:model.pkgIcon
                            pkgStatus:model.pkgStatus
                            showStatus:model.showStatus
                         }
                    }

                    Kirigami.PlaceholderMessage { 
                        id: emptyHint
                        anchors.centerIn: parent
                        width: parent.width - (Kirigami.Units.largeSpacing * 4)
                        visible: listPkg.count==0?true:false
                        text: i18nd("lliurex-up","Packages not found")
                    }

                 } 
            }
        }
          
    }

}

