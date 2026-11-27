import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

Rectangle {
    visible: true
    color: "transparent"

    ColumnLayout {
        id: loadGrid
        anchors.centerIn: parent
        width: parent.width * 0.9
        spacing: 15

        Kirigami.InlineMessage {
            id: errorLabel
            visible: true
            text: getErrorText()
            type: mainStackBridge.showErrorMessage.type === 2
                    ?Kirigami.MessageType.Warning : Kirigami.MessageType.Error
            Layout.fillWidth: true
        }
    }

    function getErrorText() {

        switch (mainStackBridge.showErrorMessage.msgCode) {
            case -1:
                return i18nd("lliurex-up","There's not enough space on disk to upgrade: 2 GB needed")+ " - " + loadStackBridge.freeSpaceAvailable + " GB " + i18nd("lliurex-up","available")
            case -2:
                return i18nd("lliurex-up","Unable to connect to lliurex.gva.es")
            case -3:
                return i18nd("lliurex-up","Unable to update Lliurex-Up. See /var/log/lliurex-up.log") + " " + mainStackBridge.showErrorMessage.data
            case -4:
                return i18nd("lliurex-up","Updated abort. An error occurred in the search for updates") + " " + mainStackBridge.showErrorMessage.data
            case -5:
                return i18nd("lliurex-up","Updated abort for incorrect metapackages detected in update")
            default:
                return ""
        }
    }
}
