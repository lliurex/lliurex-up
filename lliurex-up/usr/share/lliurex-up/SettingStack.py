#!/usr/bin/python3

from PySide2.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import threading
import signal
import copy
import time
import sys
import pwd


signal.signal(signal.SIGINT, signal.SIG_DFL)

class Bridge(QObject):

	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		Bridge.llxUpConnect=self.core.llxUpConnect
		self._showSettingsPanel=False
		self._isSystrayEnabled=False
		self._showSettingsMsg=False
	
	#def __init__

	def getSettingsInfo(self):

		self.showSettingsPanel=Bridge.llxUpConnect.manageSettingsOptions()
		self.isSystrayEnabled=Bridge.llxUpConnect.isSystrayEnabled()

	#def getSettingsInfo

	def _getShowSettingsPanel(self):

		return self._showSettingsPanel

	#def _getShowSettingsPanel

	def _setShowSettingsPanel(self,showSettingsPanel):

		if self._showSettingsPanel!=showSettingsPanel:
			self._showSettingsPanel=showSettingsPanel
			self.on_showSettingsPanel.emit()

	#def _setShowSettingsPanel

	def _getIsSystrayEnabled(self):

		return self._isSystrayEnabled

	#def _getIsSystrayEnabled

	def _setIsSystrayEnabled(self,isSystrayEnabled):

		if self._isSystrayEnabled!=isSystrayEnabled:
			self._isSystrayEnabled=isSystrayEnabled
			self.on_isSystratryEnabled.emit()

	#def _setIsSystrayEnabled

	def _getShowSettingsMsg(self):

		return self._showSettingsMsg

	#def _getShowSettinsMgs

	def _setShowSettingsMsg(self,showSettingsMsg):

		if self._showSettingsMsg!=showSettingsMsg:
			self._showSettingsMsg=showSettingsMsg
			self.on_showSettingsMsg.emit()

	#def _setShowSettingsMsg

	@Slot(bool)
	def manageSystray(self,enable):

		Bridge.llxUpConnect.manageSystray(enable)
		self.showSettingsMsg=True

	#def manageSystray


	on_showSettingsPanel=Signal()
	showSettingsPanel=Property(bool,_getShowSettingsPanel,_setShowSettingsPanel,notify=on_showSettingsPanel)
	
	on_isSystratryEnabled=Signal()
	isSystrayEnabled=Property(bool,_getIsSystrayEnabled,_setIsSystrayEnabled,notify=on_isSystratryEnabled)

	on_showSettingsMsg=Signal()
	showSettingsMsg=Property(bool,_getShowSettingsMsg,_setShowSettingsMsg,notify=on_showSettingsMsg)

#class Bridge

import Core

