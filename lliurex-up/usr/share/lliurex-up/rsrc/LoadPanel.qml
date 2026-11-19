import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    visible: true
    color: "transparent"

    ColumnLayout {
        id: loadRoot
        anchors.centerIn: parent
        width: parent.width * 0.9
        spacing: 10

        Image {
            id: spinnerImage
            source: "loading.png"
            Layout.preferredWidth: 24
            Layout.preferredHeight: 24
            Layout.alignment: Qt.AlignHCenter
            fillMode: Image.PreserveAspectFit
            smooth: false
            antialiasing: false
            rotation: 0
        }

        Timer{
            id: rotationTimer
            running: (spinnerImage !== null && loadRoot !== null) && spinnerImage.visible && loadRoot.visible
            repeat: true
            interval: 100

            onTriggered: {
                spinnerImage.rotation= (spinnerImage.rotation + 330) % 360
            }
        }

        Text {
            id: loadtext
            Layout.alignment: Qt.AlignHCenter
            text: {
                if (loadStackBridge.loadStep === 5){
                    return getMsg() + " " + loadStackBridge.countDownValue + " " + i18nd("lliurex-up","seconds")
                }
                return getMsg()
            }
        }

        ProgressBar {
            id: loadBar
            from: 0.0
            to: 1.0
            value: loadStackBridge.progressValue
            Layout.alignment: Qt.AlignHCenter
            implicitWidth: 500
        }
    }

    function getMsg(){

        const headed = loadStackBridge.loadStep + " " + i18nd("lliurex-up","of") + " " + loadStackBridge.totalSteps
        let msg = ""

        switch(loadStackBridge.loadStep){
            case 1:
                msg = i18nd("lliurex-up","Checking sytem...")
                break;
            case 2:
                msg = i18nd("lliurex-up","Executing init-actions...")
                break;
            case 3:
                msg = i18nd("lliurex-up","Looking for new version of Lliurex-Up...")
                break;
            case 4:
                msg = i18nd("lliurex-up","Updating Lliurex-Up...")
                break;
            case 5:
                return i18nd("lliurex-up","Lliurex-Up is now updated and will be reboot in ")
            case 6:
                msg = i18nd("lliurex-up","Looking for new version to update...")
                break;
            case 7:
                msg = i18nd("lliurex-up","Looking for new version available...")
                break;
            case 8:
                msg = i18nd("lliurex-up","Checking if installation of metapackage is required...")
                break;
            case 9:
                msg = i18nd("lliurex-up","Looking for new updates...")
                break;
        }
        return headed + ". " + msg
    }
}