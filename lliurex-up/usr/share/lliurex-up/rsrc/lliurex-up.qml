import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window

ApplicationWindow {
    id: mainWindow

    property bool closing: false
    property int margin: 1

    visible: true
    title: "LliureX-Up"
    color: "#eff0f1"
    width: mainLayout.implicitWidth + 2 * margin
    height: mainLayout.implicitHeight + 2 * margin
    minimumWidth: 850 + 2 * margin
    minimumHeight: 580 + 2 * margin

    Component.onCompleted: {
        x = Screen.width / 2 - width / 2
        y = Screen.height / 2 - height / 2
    }

    onClosing:(close)=> {

        close.accepted=closing;

        if (!closing) {
            mainStackBridge.closeApplication();
            closeTimer.start();
        }
    }

    Timer {
        id: closeTimer
        interval: 100
        repeat: true
        onTriggered: {
            if (mainStackBridge.closeGui) {
                stop();
                mainWindow.closing = true;
                mainWindow.close();
            }
        }
    }

    ColumnLayout {
        id: mainLayout
        anchors.fill: parent

        Rectangle {
            color: "#0049aa"
            Layout.fillWidth: true
            Layout.preferredHeight: 120

            Image {
                id: banner
                source: "lliurex-up-banner.png"
                anchors.centerIn: parent
                fillMode: Image.PreserveAspectFit  
            }
        }

        StackView {
            id: mainView
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredHeight: 460

            property int currentView: mainStackBridge.currentStack

            initialItem: loadView

            onCurrentViewChanged: {
                switch(currentView) {
                    case 0:
                        mainView.replace(loadView)
                        break;
                    case 1:
                        mainView.replace(errorView)
                        break;
                    case 2:
                        mainView.replace(applicationOptionsView)
                        break;
                }
            }

            replaceEnter: Transition {
                NumberAnimation {
                    property: "opacity"
                    from: 0
                    to: 1
                    duration: 60
                }
            }

            replaceExit: Transition {
                NumberAnimation { 
                    property: "opacity"
                    from: 1
                    to: 0
                    duration: 60
                }
            }
        }

        Component {
            id: loadView
            LoadPanel {
                id: loadPanel
            }
        }

        Component {
            id: errorView
            ErrorPanel {
                id: errorPanel
            }
        }

        Component {
            id: applicationOptionsView
            ApplicationOptions {
                id: applicationOptions
            }
        }
    }
}
