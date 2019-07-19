#!/bin/bash

xgettext --join-existing ../lliurex-up/usr/share/lliurex-up/lliurex-up.py -o ./lliurex-up/lliurex-up.pot
xgettext --join-existing ../lliurex-up/usr/share/lliurex-up/rsrc/lliurex-up.ui  -o ./lliurex-up/lliurex-up.pot
xgettext --join-existing -L python ../lliurex-up-indicator/usr/bin/lliurex-up-indicator -o ./lliurex-up/lliurex-up.pot
xgettext --join-existing -L python ../lliurex-up/usr/bin/lliurex-up-desktop-launcher.py -o ./lliurex-up/lliurex-up.pot