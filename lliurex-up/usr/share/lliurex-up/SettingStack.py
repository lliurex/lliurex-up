#!/usr/bin/python3

from PySide6.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import threading
import signal
import copy
import time
import sys
import pwd


signal.signal(signal.SIGINT, signal.SIG_DFL)

class Bridge(QObject):

	SYSTRAY_MSG=0
	AUTOUPGRADE_ENABLE_ERROR=-1
	AUTOUPGRADE_DISABLE_ERROR=-2
	AUTOUPGRADE_ENABLE=1
	AUTOUPGRADE_DISABLE=2

	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		Bridge.llxUpConnect=self.core.llxUpConnect
		self._showSettingsPanel=False
		self._isSystrayEnabled=False
		self._isAutoUpgradeAvailable=False
		self._isAutoUpgradeEnabled=False
		self._showSettingsMsg=[False,"","Ok"]
		self._isAutoUpgradeRun=False
	
	#def __init__

	def getSettingsInfo(self):

		self.showSettingsPanel=Bridge.llxUpConnect.manageSettingsOptions()
		self.isSystrayEnabled=Bridge.llxUpConnect.isSystrayEnabled()
		self.isAutoUpgradeAvailable=Bridge.llxUpConnect.isAutoUpgradeAvailable()
		if self.isAutoUpgradeAvailable:
			self.isAutoUpgradeEnabled=Bridge.llxUpConnect.isAutoUpgradeEnabled()
			self.isAutoUpgradeRun=Bridge.llxUpConnect.isAutoUpgradeRun()

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

	def _getIsAutoUpgradeAvailable(self):

		return self._isAutoUpgradeAvailable

	#def _getIsAutoUpgradeAvailable

	def _setIsAutoUpgradeAvailable(self,isAutoUpgradeAvailable):

		if self._isAutoUpgradeAvailable!=isAutoUpgradeAvailable:
			self._isAutoUpgradeAvailable=isAutoUpgradeAvailable
			self.on_isAutoUpgradeAvailable.emit()

	#def _setIsAutoUpgradeAvailable

	def _getIsAutoUpgradeEnabled(self):

		return self._isAutoUpgradeEnabled

	#def _getIsAutoUpgradeEnabled

	def _setIsAutoUpgradeEnabled(self,isAutoUpgradeEnabled):

		if self._isAutoUpgradeEnabled!=isAutoUpgradeEnabled:
			self._isAutoUpgradeEnabled=isAutoUpgradeEnabled
			self.on_isAutoUpgradeEnabled.emit()

	#def _setIsAutoUpgradeEnabled

	def _getShowSettingsMsg(self):

		return self._showSettingsMsg

	#def _getShowSettinsMgs

	def _setShowSettingsMsg(self,showSettingsMsg):

		if self._showSettingsMsg!=showSettingsMsg:
			self._showSettingsMsg=showSettingsMsg
			self.on_showSettingsMsg.emit()

	#def _setShowSettingsMsg

	def _getIsAutoUpgradeRun(self):

		return self._isAutoUpgradeRun

	#def _getIsAutoUpgradeRun

	def _setIsAutoUpgradeRun(self,isAutoUpgradeRun):

		if self._isAutoUpgradeRun!=isAutoUpgradeRun:
			self._isAutoUpgradeRun=isAutoUpgradeRun
			self.on_isAutoUpgradeRun.emit()

	#def _setIsAutoUpgradeRun

	@Slot(bool)
	def manageSystray(self,enable):

		Bridge.llxUpConnect.manageSystray(enable)
		self.showSettingsMsg=[True,Bridge.SYSTRAY_MSG,"Ok"]

	#def manageSystray

	@Slot(bool)
	def manageAutoUpgrade(self,enable):
		
		ret=Bridge.llxUpConnect.manageAutoUpgrade(enable)
		if enable:
			if ret:
				self.showSettingsMsg=[True,Bridge.AUTOUPGRADE_ENABLE,"Ok"]
			else:
				self.showSettingsMsg=[True,Bridge.AUTOUPGRADE_ENABLE_ERROR,"Error"]
		else:
			if ret:
				self.showSettingsMsg=[True,Bridge.AUTOUPGRADE_DISABLE,"Ok"]
			else:
				self.showSettingsMsg=[True,Bridge.AUTOUPGRADE_DISABLE_ERROR,"Error"]

	#def manageAutoUpgtade 
		
	on_showSettingsPanel=Signal()
	showSettingsPanel=Property(bool,_getShowSettingsPanel,_setShowSettingsPanel,notify=on_showSettingsPanel)
	
	on_isSystratryEnabled=Signal()
	isSystrayEnabled=Property(bool,_getIsSystrayEnabled,_setIsSystrayEnabled,notify=on_isSystratryEnabled)

	on_isAutoUpgradeAvailable=Signal()
	isAutoUpgradeAvailable=Property(bool,_getIsAutoUpgradeAvailable,_setIsAutoUpgradeAvailable,notify=on_isAutoUpgradeAvailable)
	
	on_isAutoUpgradeEnabled=Signal()
	isAutoUpgradeEnabled=Property(bool,_getIsAutoUpgradeEnabled,_setIsAutoUpgradeEnabled,notify=on_isAutoUpgradeEnabled)

	on_showSettingsMsg=Signal()
	showSettingsMsg=Property('QVariantList',_getShowSettingsMsg,_setShowSettingsMsg,notify=on_showSettingsMsg)

	on_isAutoUpgradeRun=Signal()
	isAutoUpgradeRun=Property(bool,_getIsAutoUpgradeRun,_setIsAutoUpgradeRun,notify=on_isAutoUpgradeRun)

#class Bridge

import Core

