import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQml.Models 2.8
//import org.kde.plasma.components 3.0 as PC3
import org.kde.kirigami 2.16 as Kirigami
import QtQuick.Layouts 1.15


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

        //PC3.TextField{
        TextField{
            id:pkgSearchEntry
            font.pointSize:10
            horizontalAlignment:TextInput.AlignLeft
            Layout.alignment:Qt.AlignRight
            Layout.topMargin:40
            focus:true
            width:100
            //placeholderText:i18nd("lliurex-up","Search...")
            placeholderText:"Search..."
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

            //PC3.ScrollView{
            ScrollView{
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
                        //width: parent.width - (.units.largeSpacing * 4)
                        width: parent.width
                        visible: listPkg.count==0?true:false
                        //text: i18nd("lliurex-up","Packages not found")
                        text: "Packages not found"
                    }

                 } 
            }
        }
          
    }

}

