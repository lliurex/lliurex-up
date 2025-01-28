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
		self._isWeekPauseActive=False
		self._canExtendedPause=False
		self._weeksOfPause=Bridge.llxUpConnect.weeksOfPause
		self._weeksOfPauseCombo=Bridge.llxUpConnect.weeksOfPauseCombo
		self._extensionPauseCombo=Bridge.llxUpConnect.extensionPauseCombo
		self.initialConfig=copy.deepcopy(Bridge.llxUpConnect.currentConfig)

	#def __init__

	def getSettingsInfo(self):

		self.showSettingsPanel=Bridge.llxUpConnect.manageSettingsOptions()
		self.isSystrayEnabled=Bridge.llxUpConnect.isSystrayEnabled
		self.isAutoUpgradeAvailable=Bridge.llxUpConnect.isAutoUpgradeAvailable
		self.isAutoUpgradeEnabled=Bridge.llxUpConnect.isAutoUpgradeEnabled
		if self.isAutoUpgradeEnabled:
			self.isAutoUpgradeRun=Bridge.llxUpConnect.isAutoUpgradeRun()
			self.weeksOfPause=Bridge.llxUpConnect.weeksOfPause
			self.isWeekPauseActive=Bridge.llxUpConnect.isWeekPauseActive
			self.canExtendedPause=Bridge.llxUpConnect.canExtendedPause
			self.extensionPauseCombo=Bridge.llxUpConnect.extensionPauseCombo
		self.initialConfig=copy.deepcopy(Bridge.llxUpConnect.currentConfig)
		
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

	def _getIsWeekPauseActive(self):

		return self._isWeekPauseActive

	#def _getIsWeekPauseActive

	def _setIsWeekPauseActive(self,isWeekPauseActive):

		if self._isWeekPauseActive!=isWeekPauseActive:
			self._isWeekPauseActive=isWeekPauseActive
			self.on_isWeekPauseActive.emit()

	#def _setIsWeekPauseActive

	def _getWeekOfPause(self):

		return self._weeksOfPause

	#def _getCanExtendedPause

	def _setWeeksOfPause(self,weeksOfPause):

		if self._weeksOfPause!=weeksOfPause:
			self._weeksOfPause=weeksOfPause
			self.on_weeksOfPause.emit()

	#def _setWeeksOfPause

	def _getCanExtendedPause(self):

		return self._canExtendedPause

	#def _getCanExtendedPause

	def _setCanExtendedPause(self,canExtendedPause):

		if self._canExtendedPause!=canExtendedPause:
			self._canExtendedPause=canExtendedPause
			self.on_canExtendePause.emit()

	#def _setCanExtendedPause

	def _getWeeksOfPauseCombo(self):

		return self._weeksOfPauseCombo

	#def _getWeeksOfPauseCombo

	def _getExtensionPauseCombo(self):

		return self._extensionPauseCombo

	#def _getWeeksOfPauseCombo

	def _setExtensionPauseCombo(self,extensionPauseCombo):

		if self._extensionPauseCombo!=extensionPauseCombo:
			self._extensionPauseCombo=extensionPauseCombo
			self.on_extensionPauseCombo.emit()

	#def _setExtensionPauseCombo

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

	on_isWeekPauseActive=Signal()
	isWeekPauseActive=Property(bool,_getIsWeekPauseActive,_setIsWeekPauseActive,notify=on_isWeekPauseActive)

	on_weeksOfPause=Signal()
	weeksOfPause=Property(int,_getWeekOfPause,_setWeeksOfPause,notify=on_weeksOfPause)
	
	on_canExtendePause=Signal()
	canExtendedPause=Property(int,_getCanExtendedPause,_setCanExtendedPause,notify=on_canExtendePause)	

	on_extensionPauseCombo=Signal()
	extensionPauseCombo=Property('QVariant',_getExtensionPauseCombo,_setExtensionPauseCombo,notify=on_extensionPauseCombo)

	weeksOfPauseCombo=Property('QVariant',_getWeeksOfPauseCombo,constant=True)
	
#class Bridge

import Core

