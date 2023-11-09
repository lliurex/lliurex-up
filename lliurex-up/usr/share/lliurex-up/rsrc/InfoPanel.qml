import org.kde.plasma.core 2.0 as PlasmaCore
import org.kde.kirigami 2.16 as Kirigami
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15


Rectangle{
    color:"transparent"

    Text{ 
        text:i18nd("lliurex-up","Update information")
        font.family: "Quattrocento Sans Bold"
        font.pointSize: 16
    }
    GridLayout{
        id:infoLayout
        rows:1
        flow: GridLayout.TopToBottom
        rowSpacing:10
        anchors.left:parent.left
        width:parent.width-10

        GridLayout{
            id: updateInfo
            columns: 2
            flow: GridLayout.LeftToRight
            columnSpacing:10
            Layout.alignment:Qt.AlignHCenter
            Layout.topMargin:50

            Text{
                id:currentVersionText
                Layout.bottomMargin:10
                Layout.alignment:Qt.AlignRight
                text:i18nd("lliurex-up","Current version:")
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 10
            }

            Text{
                id:currentVersionValue
                text:{
                    if (infoStackBridge.currentVersion!=""){
                        infoStackBridge.currentVersion
                    }else{
                        i18nd("lliurex-up","Not available")
                    }
                }
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 10
                Layout.alignment:Qt.AlignLeft
                Layout.bottomMargin:10
            }
          
            Text{
                id:availableVersionText
                Layout.bottomMargin:10
                Layout.alignment:Qt.AlignRight
                text:i18nd("lliurex-up","Available version (lliurex.net):")
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 10
            }

            Text{
                id:availableVersionValue
                text:{
                    if (infoStackBridge.availableVersion=="Client"){
                        i18nd("lliurex-up","Not available for clients")
                    }else{
                        if (infoStackBridge.availableVersion=="Connection"){
                            i18nd("lliurex-up","Not available. Check conexion to lliurex.net")
                        }else{
                            infoStackBridge.availableVersion
                        }
                    }
                }
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 10
                Layout.alignment:Qt.AlignLeft
                Layout.bottomMargin:10
            }

            Text{
                id:candiateVersionText
                Layout.bottomMargin:10
                Layout.alignment:Qt.AlignRight
                text:i18nd("lliurex-up","Candidate version (to install):")
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 10
            }

            Text{
                id:candiateVersionValue
                text:{
                    if (infoStackBridge.candidateVersion!=""){
                        infoStackBridge.candidateVersion
                    }else{
                        i18nd("lliurex-up","Not available")
                    }
                }
                Layout.maximumWidth:390
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 10
                Layout.alignment:Qt.AlignLeft
                Layout.bottomMargin:10
            }

            Text{
                id:numberPackagesText
                Layout.bottomMargin:10
                Layout.alignment:Qt.AlignRight
                text:i18nd("lliurex-up","Number of packages:")
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 10
            }

            Text{
                id:numberPackagesValue
                text:infoStackBridge.packagesToUpdate+" ( "+infoStackBridge.newPackagesToUpdate+ " "+i18nd("lliurex-up","news")+" )"
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 10
                Layout.alignment:Qt.AlignLeft
                Layout.bottomMargin:10
            }

            Text{
                id:sizeText
                Layout.bottomMargin:10
                Layout.alignment:Qt.AlignRight
                text:i18nd("lliurex-up","Size of update (aprox):")
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 10
            }

            Text{
                id:sizeValue
                text:infoStackBridge.updateSize
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 10
                Layout.alignment:Qt.AlignLeft
                Layout.bottomMargin:10
            }
           
            Text{
                id:sourceText
                text:i18nd("lliurex-up","Update source:")
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 10
                Layout.alignment:Qt.AlignRight
                Layout.bottomMargin:10
            }

            Text{
                id:sourceTextValue
                text:{
                    if (infoStackBridge.updateSource!=""){
                        infoStackBridge.updateSource
                    }else{
                        i18nd("lliurex-up","Not available")
                    }
                }
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 10
                Layout.alignment:Qt.AlignLeft
                Layout.bottomMargin:10
            }
      
        }
    }
   
}



