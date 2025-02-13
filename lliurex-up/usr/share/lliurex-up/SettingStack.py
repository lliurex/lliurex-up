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

class ApplyChanges(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		self.core=Core.Core.get_core()
		self.llxUpConnect=self.core.llxUpConnect
		self.newConfig=args[0]
		self.ret=[]

	#def __init__

	def run(self,*args):
		
		self.ret=self.llxUpConnect.applySettingsChanges(self.newConfig)

	#def run

#class SetChanges

class Bridge(QObject):

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
		self._canPauseUpdate=False
		self._isWeekPauseActive=False
		self._canExtendedPause=False
		self._weeksOfPause=Bridge.llxUpConnect.weeksOfPause
		self._weeksOfPauseCombo=Bridge.llxUpConnect.weeksOfPauseCombo
		self._extensionPauseCombo=Bridge.llxUpConnect.extensionPauseCombo
		self._settingsChanged=False
		self._showExtensionPauseCombo=False
		self._dateToUpdate=datetime.date.fromisoformat(Bridge.llxUpConnect.dateToUpdate).strftime("%d/%m/%y")
		self._isAdmin=Bridge.llxUpConnect.checkUser()
		self._extensionWeekPause=Bridge.llxUpConnect.extensionWeekPause
		self.initialConfig=copy.deepcopy(Bridge.llxUpConnect.currentConfig)
		
	#def __init__

	def getSettingsInfo(self):

		self.showSettingsPanel=Bridge.llxUpConnect.manageSettingsOptions()
		self.isSystrayEnabled=Bridge.llxUpConnect.isSystrayEnabled
		self.isAutoUpgradeAvailable=Bridge.llxUpConnect.isAutoUpgradeAvailable
		self.isAutoUpgradeEnabled=Bridge.llxUpConnect.isAutoUpgradeEnabled
		self.extensionWeekPause=Bridge.llxUpConnect.extensionWeekPause
		
		if self.isAutoUpgradeEnabled:
			self.isAutoUpgradeRun=Bridge.llxUpConnect.isAutoUpgradeRun()
		
		self.canPauseUpdate=Bridge.llxUpConnect.canPauseUpdate
		self.weeksOfPause=Bridge.llxUpConnect.weeksOfPause
		self.isWeekPauseActive=Bridge.llxUpConnect.isWeekPauseActive
		self.canExtendedPause=Bridge.llxUpConnect.canExtendedPause
		self.extensionPauseCombo=Bridge.llxUpConnect.extensionPauseCombo
		self.dateToUpdate=datetime.date.fromisoformat(Bridge.llxUpConnect.dateToUpdate).strftime("%d/%m/%y")
		
		self.showExtensionPauseCombo=False
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

	def _getCanPauseUpdate(self):

		return self._canPauseUpdate

	#def _getCanPauseUpdate

	def _setCanPauseUpdate(self,canPauseUpdate):

		if self._canPauseUpdate!=canPauseUpdate:
			self._canPauseUpdate=canPauseUpdate
			self.on_canPauseUpdate.emit()

	#def _setIsWeekPauseActive

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

	def _getShowExtensionPauseCombo(self):

		return self._showExtensionPauseCombo

	#def _getShowExtensionPauseCombo

	def _setShowExtensionPauseCombo(self,showExtensionPauseCombo):

		if self._showExtensionPauseCombo!=showExtensionPauseCombo:
			self._showExtensionPauseCombo=showExtensionPauseCombo
			self.on_showExtensionPauseCombo.emit()

	#def _setShowExtensionPauseCombo

	def _getExtensionWeekPause(self):

		return self._extensionWeekPause

	#def _getExtensionWeekPause

	def _setExtensionWeekPause(self,extensionWeekPause):

		if self._extensionWeekPause!=extensionWeekPause:
			self._extensionWeekPause=extensionWeekPause
			self.on_extensionWeekPause.emit()

	#def _setExtensionWeekPause

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

	def _getSettingsChanged(self):

		return self._settingsChanged

	#def _getSettingsChanged 

	def _setSettingsChanged(self,settingsChanged):

		if self._settingsChanged!=settingsChanged:
			self._settingsChanged=settingsChanged
			self.on_settingsChanged.emit()

	#def _setSettingsChanged 

	def _getDateToUpdate(self):

		return self._dateToUpdate

	#def _getDateToUpdate

	def _setDateToUpdate(self,dateToUpdate):

		if self._dateToUpdate!=dateToUpdate:
			self._dateToUpdate=dateToUpdate
			self.on_dateToUpdate.emit()

	#def _setDateToUpdate

	def _getIsAdmin(self):

		return self._isAdmin

	#def _getIsAdmin

	@Slot(bool)
	def manageSystray(self,enable):

		if enable!=self.isSystrayEnabled:
			self.isSystrayEnabled=enable
			self.initialConfig[0]=enable

		if self.initialConfig!=Bridge.llxUpConnect.currentConfig:
			self.settingsChanged=True
		else:
			self.settingsChanged=False

	#def manageSystray

	@Slot(bool)
	def manageAutoUpgrade(self,value):
		
		self.showSettingsMsg=[False,"","Ok"]
		
		if value!=self.isAutoUpgradeEnabled:
			self.isAutoUpgradeEnabled=value
			self.initialConfig[1]=value
		
		if self.initialConfig!=Bridge.llxUpConnect.currentConfig:
			self.settingsChanged=True
		else:
			self.settingsChanged=False

	#def manageAutoUpgtade 

	@Slot(bool)
	def manageUpdatePause(self,value):

		self.showSettingsMsg=[False,"","Ok"]
		if value!=self.isWeekPauseActive:
			self.isWeekPauseActive=value
			self.initialConfig[2]=value

		if self.initialConfig!=Bridge.llxUpConnect.currentConfig:
			self.settingsChanged=True
		else:
			self.settingsChanged=False

		self.showExtensionPauseCombo=False

	#def manageUpdatePause

	@Slot(int)
	def manageWeeksOfPause(self,value):

		self.showSettingsMsg=[False,"","Ok"]

		if value!=self.weeksOfPause:
			self.weeksOfPause=value
			self.initialConfig[3]=value

		if self.initialConfig!=Bridge.llxUpConnect.currentConfig:
			self.settingsChanged=True
		else:
			self.settingsChanged=False

	#def manageWeeksOfPause

	@Slot(bool)
	def manageExtensionPauseBtn(self,isVisible):

		if isVisible:
			self.showExtensionPauseCombo=False
		else:
			self.showExtensionPauseCombo=True

	#def manageExtensionPauseBtn

	@Slot(int)
	def manageExtensionPause(self,value):

		if value!=self.extensionWeekPause:
			self.extensionWeekPause=value
			self.initialConfig[4]=value

		if self.initialConfig!=Bridge.llxUpConnect.currentConfig:
			self.settingsChanged=True
		else:
			self.settingsChanged=False

	#def manageExtensionPause

	@Slot()
	def applyChanges(self):
		
		self.core.mainStack.closePopUp=False
		self.core.mainStack.closeGui=False
		self.showSettingsMsg=[False,"","Ok"]
		self.applyChangesT=ApplyChanges(self.initialConfig)
		self.applyChangesT.start()
		self.applyChangesT.finished.connect(self._applyChangesRet)

	#def applyChanges

	def _applyChangesRet(self):

		self.getSettingsInfo()
		self.settingsChanged=False
		self.core.mainStack.closePopUp=True

		if not self.applyChangesT.ret[0]:
			self.core.mainStack.closeGui=True
			self.showSettingsMsg=[True,self.applyChangesT.ret[1],"Ok"]
			if self.core.mainStack.moveToStack !="":
				self.core.mainStack.manageTransitions(self.core.mainStack.moveToStack)
		else:
			self.core.mainStack.moveToStack=""
			self.showSettingsMsg=[True,self.applyChangesT.ret[1],"Error"]

	
	#def _applyChangesRet

	@Slot()
	def discardChanges(self):

		self.core.mainStack.closePopUp=False
		self.core.mainStack.closeGui=False
		self.showSettingsMsg=[False,"","Ok"]
		self._discardChangesRet()

	#def discardChanges

	def _discardChangesRet(self):

		self.getSettingsInfo()
		self.core.mainStack.closePopUp=True
		self.settingsChanged=False
		self.core.mainStack.closeGui=True
		if self.core.mainStack.moveToStack !="":
			self.core.mainStack.manageTransitions(self.core.mainStack.moveToStack)

	# def _discardChangesRet


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

	on_canPauseUpdate=Signal()
	canPauseUpdate=Property(bool,_getCanPauseUpdate,_setCanPauseUpdate,notify=on_canPauseUpdate)

	on_isWeekPauseActive=Signal()
	isWeekPauseActive=Property(bool,_getIsWeekPauseActive,_setIsWeekPauseActive,notify=on_isWeekPauseActive)

	on_weeksOfPause=Signal()
	weeksOfPause=Property(int,_getWeekOfPause,_setWeeksOfPause,notify=on_weeksOfPause)
	
	on_canExtendePause=Signal()
	canExtendedPause=Property(int,_getCanExtendedPause,_setCanExtendedPause,notify=on_canExtendePause)	

	on_extensionPauseCombo=Signal()
	extensionPauseCombo=Property('QVariant',_getExtensionPauseCombo,_setExtensionPauseCombo,notify=on_extensionPauseCombo)

	on_showExtensionPauseCombo=Signal()
	showExtensionPauseCombo=Property(bool,_getShowExtensionPauseCombo,_setShowExtensionPauseCombo,notify=on_showExtensionPauseCombo)

	on_extensionWeekPause=Signal()
	extensionWeekPause=Property(int,_getExtensionWeekPause,_setExtensionWeekPause,notify=on_extensionWeekPause)
	
	on_settingsChanged=Signal()
	settingsChanged=Property(bool,_getSettingsChanged,_setSettingsChanged,notify=on_settingsChanged)

	on_dateToUpdate=Signal()
	dateToUpdate=Property(str,_getDateToUpdate,_setDateToUpdate,notify=on_dateToUpdate)

	isAdmin=Property(bool,_getIsAdmin,constant=True)

	weeksOfPauseCombo=Property('QVariant',_getWeeksOfPauseCombo,constant=True)
	
#class Bridge

import Core

