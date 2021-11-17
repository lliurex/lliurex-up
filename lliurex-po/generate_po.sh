#!/bin/bash

xgettext --join-existing ../lliurex-up/usr/share/lliurex-up/MainWindow.py -o ./lliurex-up/lliurex-up.pot
xgettext --join-existing ../lliurex-up/usr/share/lliurex-up/LoadBox.py -o ./lliurex-up/lliurex-up.pot
xgettext --join-existing ../lliurex-up/usr/share/lliurex-up/InformationBox.py -o ./lliurex-up/lliurex-up.pot
xgettext --join-existing ../lliurex-up/usr/share/lliurex-up/OptionsBox.py -o ./lliurex-up/lliurex-up.pot
xgettext --join-existing ../lliurex-up/usr/share/lliurex-up/PackagesBox.py -o ./lliurex-up/lliurex-up.pot
xgettext --join-existing ../lliurex-up/usr/share/lliurex-up/TerminalBox.py -o ./lliurex-up/lliurex-up.pot
xgettext --join-existing ../lliurex-up/usr/share/lliurex-up/PreferencesBox.py -o ./lliurex-up/lliurex-up.pot
xgettext --join-existing ../lliurex-up/usr/share/lliurex-up/rsrc/lliurex-up.ui  -o ./lliurex-up/lliurex-up.pot
xgettext --join-existing -L python ../lliurex-up-indicator/usr/bin/lliurex-up-indicator -o ./lliurex-up/lliurex-up.pot
xgettext --join-existing -L python ../lliurex-up/usr/bin/lliurex-up-desktop-launcher.py -o ./lliurex-up/lliurex-up.pot