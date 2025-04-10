#!/usr/bin/python3

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QUrl
from PySide6.QtGui import QIcon
from PySide6.QtQml import QQmlApplicationEngine

import sys
import os

import LaunchStack
launchStack=LaunchStack.Bridge()
ret=launchStack.canRunUpdate()

if not ret:
	app = QApplication()
	app.setDesktopFileName("lliurex-up")
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
	app.setDesktopFileName("lliurex-up")
	engine = QQmlApplicationEngine()
	engine.clearComponentCache()
	context=engine.rootContext()
	mainStackBridge=c.mainStack
	loadStackBridge=c.loadStack
	infoStackBridge=c.infoStack
	packageStackBridge=c.packageStack
	settingStackBridge=c.settingStack
	context.setContextProperty("mainStackBridge",mainStackBridge)
	context.setContextProperty("loadStackBridge",loadStackBridge)
	context.setContextProperty("infoStackBridge",infoStackBridge)
	context.setContextProperty("packageStackBridge",packageStackBridge)
	context.setContextProperty("settingStackBridge",settingStackBridge)

	url = QUrl("/usr/share/lliurex-up/rsrc/lliurex-up.qml")


engine.load(url)
if not engine.rootObjects():
	sys.exit(-1)

engine.quit.connect(QApplication.quit)
ret=app.exec()
del engine
del app

sys.exit(ret)	



