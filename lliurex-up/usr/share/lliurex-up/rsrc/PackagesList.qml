import QtQuick
import QtQuick.Controls
import QtQml.Models
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

Rectangle {
    id: pkgGrid
    property alias packagesModel: filterModel.model
    property alias listCount: listPkg.count
    color: "transparent"

    ColumnLayout {
        anchors.fill: parent
        spacing: 10

        RowLayout {
            id: filterRow
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignRight
            spacing: 10
            enabled: true

            TextField {
                id: pkgSearchEntry
                font.pointSize: 10
                horizontalAlignment: TextInput.AlignLeft
                Layout.alignment: Qt.AlignRight
                focus: true
                width: 100
                placeholderText: i18nd("lliurex-up","Search...")
                onTextChanged: filterModel.update()
            }
        }

        Rectangle {
            id: pkgTable
            visible: true
            Layout.fillHeight: true
            Layout.fillWidth: true
            color: "white"
            border.color: "#d3d3d3"

            ScrollView {
                anchors.fill: parent

                ListView {
                    id: listPkg

                    Timer {
                        id: searchTimer
                        interval: 150
                        repeat: false
                        onTriggered: filterModel.update()
                    }

                    model: FilterDelegateModel {
                        id: filterModel
                        model: packagesModel
                        role: "pkgId"
                        search: pkgSearchEntry.text.trim()
                        externalTimer: searchTimer

                        delegate: ListDelegatePkgItem {
                            width: pkgTable.width -18
                            pkgId: model.pkgId
                            pkgVersion: model.pkgVersion
                            pkgSize: model.pkgSize
                            pkgIcon: model.pkgIcon
                            pkgStatus: model.pkgStatus
                            showStatus: model.showStatus
                        }
                    }

                    currentIndex: -1
                    enabled: true
                    clip: true
                    focus: true
                    boundsBehavior: Flickable.StopAtBounds
                    highlightFollowsCurrentItem: true
                    highlightMoveDuration: 0
                    highlightResizeDuration: 0

                    Kirigami.PlaceholderMessage {
                        id: emptyHint
                        anchors.centerIn: parent
                        width: parent.width - (Kirigami.Units.largeSpacing * 4)
                        visible: listPkg.count === 0 ? true : false
                        text: i18nd("lliurex-up","Packages not found")
                        icon.name: "lliurex-up"
                    }
                }
            }
        }
    }
}