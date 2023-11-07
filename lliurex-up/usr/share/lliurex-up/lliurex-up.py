#!/usr/bin/python3

from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QUrl
from PySide2.QtGui import QIcon
from PySide2.QtQml import QQmlApplicationEngine

import sys
import os

import LaunchStack
launchStack=LaunchStack.Bridge()
ret=launchStack.canRunUpdate()

if not ret:
	app = QApplication()
	engine = QQmlApplicationEngine()
	engine.clearComponentCache()
	context=engine.rootContext()
	launchStackBridge=launchStack

	context.setContextProperty("launchStackBridge", launchStackBridge)

	url = QUrl("/usr/share/lliurex-up/rsrc/lliurex-up-dialog.qml")
	
else:
	import Core
	c=Core.Core.get_core()
	app = QApplication()
	engine = QQmlApplicationEngine()
	engine.clearComponentCache()
	context=engine.rootContext()
	mainStackBridge=c.mainStack
	context.setContextProperty("mainStackBridge",mainStackBridge)

	url = QUrl("/usr/share/lliurex-up/rsrc/lliurex-up.qml")


engine.load(url)
if not engine.rootObjects():
	sys.exit(-1)

engine.quit.connect(QApplication.quit)
app.setWindowIcon(QIcon("/usr/share/icons/hicolor/scalable/apps/lliurex-up.svg"));
ret=app.exec_()
del engine
del app

sys.exit(ret)	



