#!/usr/bin/python3

from PySide6.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import threading
import signal
import copy
import datetime
import sys
import pwd


signal.signal(signal.SIGINT, signal.SIG_DFL)

class ApplyChanges(QObject):

	finished = Signal(dict)
	
	def __init__(self,manager,newConfig):

		super().__init__()
		self.manager = manager
		self.newConfig = newConfig
	
	#def __init__

	def run(self,*args):
		
		ret = self.manager.applySettingsChanges(self.newConfig)

		self.finished.emit(ret)

	#def run

#class SetChanges

class Bridge(QObject):

	showSettingsPanelChanged = Signal()
	isSystratryEnabledChanged=Signal()
	showSettingsMsgChanged = Signal()
	changesInSettingsChanged = Signal()

	def __init__(self):

		QObject.__init__(self)
		self.core = Core.Core.get_core()
		self.llxUpConnect = self.core.llxUpConnect
		self._showSettingsPanel = False
		self._isSystrayEnabled =False
		self._showSettingsMsg = {"show":False,"msgCode":"","type":""}
		self._changesInSettings=False
		self.initialConfig=copy.deepcopy(self.llxUpConnect.currentConfig)
		
	#def __init__

	@Property(bool, notify = showSettingsPanelChanged)
	def showSettingsPanel(self):

		return self._showSettingsPanel

	#def showSettingsPanel

	@showSettingsPanel.setter
	def showSettingsPanel(self,showSettingsPanel):

		if self._showSettingsPanel != showSettingsPanel:
			self._showSettingsPanel = showSettingsPanel
			self.showSettingsPanelChanged.emit()

	#def showSettingsPanel

	@Property(bool, notify = isSystratryEnabledChanged)
	def isSystrayEnabled(self):

		return self._isSystrayEnabled

	#def isSystrayEnabled

	@isSystrayEnabled.setter
	def isSystrayEnabled(self,isSystrayEnabled):

		if self._isSystrayEnabled != isSystrayEnabled:
			self._isSystrayEnabled = isSystrayEnabled
			self.isSystratryEnabledChanged.emit()

	#def isSystrayEnabled

	@Property(dict, notify = showSettingsMsgChanged)
	def showSettingsMsg(self):

		return self._showSettingsMsg

	#def showSettinsMgs

	@showSettingsMsg.setter
	def showSettingsMsg(self,showSettingsMsg):

		if self._showSettingsMsg != showSettingsMsg:
			self._showSettingsMsg = showSettingsMsg
			self.showSettingsMsgChanged.emit()

	#def showSettingsMsg

	@Property(bool, notify = changesInSettingsChanged)
	def changesInSettings(self):

		return self.changesInSettings

	#def changesInSettings 

	@changesInSettings.setter
	def changesInSettings(self,changesInSettings):

		if self._changesInSettings != changesInSettings:
			self._changesInSettings = changesInSettings
			self.changesInSettingsChanged.emit()

	#def changesInSettings 


	def getSettingsInfo(self):

		self.showSettingsPanel =self.llxUpConnect.manageSettingsOptions()
		self.isSystrayEnabled = self.llxUpConnect.isSystrayEnabled
		self.initialConfig=copy.deepcopy(self.llxUpConnect.currentConfig)
	
	#def getSettingsInfo

	@Slot(bool)
	def manageSystray(self,enable):

		if enable != self.isSystrayEnabled:
			self.isSystrayEnabled = enable
			self.initialConfig["isSystrayEnabled"] = enable

		if self.initialConfig != self.llxUpConnect.currentConfig:
			self.changesInSettings = True
		else:
			self.changesInSettings = False

	#def manageSystray

	@Slot()
	def applyChanges(self):
		
		self.core.mainStack.closePopUp = False
		self.core.mainStack.closeGui = False
		self.showSettingsMsg = {"show":False,"msgCode":"","type":""}

		self.applyChangesThread = QThread()
		self.applyChangesWorker = ApplyChanges(self.llxUpConnect,self.initialConfig)
		self.applyChangesWorker.moveToThread(self.applyChangesThread)
		self.applyChangesThread.started.connect(self.applyChangesWorker.run)

		self.applyChangesWorker.finished.connect(self._applyChangesRet)
		self.applyChangesWorker.finished.connect(self.applyChangesThread.quit)
		self.applyChangesWorker.finished.connect(self.applyChangesWorker.deleteLater)
		self.applyChangesThread.finished.connect(self.applyChangesThread.deleteLater)

		self.applyChangesThread.start()

	#def applyChanges

	@Slot(dict)
	def _applyChangesRet(self,ret):

		self.getSettingsInfo()
		self.changesInSettings = False
		self.core.mainStack.closePopUp = True

		self.showSettingsMsg = {"show":True,"msgCode": ret.get("code"), "type": ret.get("type")}

		if not ret.get("status"):
			self.core.mainStack.moveToStack = ""
			return

		self.core.mainStack.closeGui = True

		if self.core.mainStack.moveToStack != "":
			self.core.mainStack.manageTransitions(self.core.mainStack.moveToStack)
	
	#def _applyChangesRet

	@Slot()
	def discardChanges(self):

		self.core.mainStack.closePopUp = False
		self.core.mainStack.closeGui = False
		self.showSettingsMsg = {"show":False,"msgCode":"","type":""}
		self._discardChangesRet()

	#def discardChanges

	def _discardChangesRet(self):

		self.getSettingsInfo()
		self.core.mainStack.closePopUp = True
		self.changesInSettings = False
		self.core.mainStack.closeGui = True
		if self.core.mainStack.moveToStack != "":
			self.core.mainStack.manageTransitions(self.core.mainStack.moveToStack)

	# def _discardChangesRet

	
#class Bridge

import Core

