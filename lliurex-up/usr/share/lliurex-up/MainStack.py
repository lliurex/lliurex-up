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

	UPDATE_OK=1
	UPDATE_NO_REQUIRED=2
	UPDATE_ERROR=-1

	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		Bridge.llxUpConnect=self.core.llxUpConnect
		self._currentStack=0
		self._showErrorMessage=["","Warning"]
		self._currentOptionStack=0
		self._showProgressBar=False
		self._progressBarValue=0.0
		self._totalUpdateSteps=4
		self._updateStep=0
		self._showUpdateBtn=False
		self._enableUpdateBtn=False
		self._showFeedbackMessage=[False,"","Ok"]
		self._updateRequired=False
		self._closeGui=False

	#def __init__

	def initBridge(self):

		Bridge.llxUpConnect.startLliurexUp()
		self.core.loadStack.checkSystem()		

	#def initBridge

	def loadInfo(self):

		self.core.infoStack.getUpdateInfo()
		self.core.packageStack.getPackagesInfo()
		self.core.settingStack.getSettingsInfo()

		if self.updateRequired:
			self.showUpdateBtn=True
			self.enableUpdateBtn=True
		else:
			self.showFeedbackMessage=[True,Bridge.UPDATE_NO_REQUIRED,"Info"]
		
		self.currentStack=2
			
	#def loadInfo

	def _getCurrentStack(self):

		return self._currentStack

	#def _getCurrentStack

	def _setCurrentStack(self,currentStack):

		if self._currentStack!=currentStack:
			self._currentStack=currentStack
			self.on_currentStack.emit()

	#def _setCurrentStack

	def _getShowErrorMessage(self):

		return self._showErrorMessage

	#def _getShowErrorMessage

	def _setShowErrorMessage(self,showErrorMessage):

		if self._showErrorMessage!=showErrorMessage:
			self._showErrorMessage=showErrorMessage
			self.on_showErrorMessage.emit()

	#def _setShowErrorMessage

	def _getCurrentOptionStack(self):

		return self._currentOptionStack

	#def _getCurrentOptionStack

	def _setCurrentOptionStack(self,currentOptionStack):

		if self._currentOptionStack!=currentOptionStack:
			self._currentOptionStack=currentOptionStack
			self.on_currentOptionStack.emit()

	#def _setCurrentOptionStack

	def _getShowProgessBar(self):

		return self._showProgressBar

	#def _getShowProgressBar

	def _setShowProgressBar(self,showProgressBar):

		if self._showProgressBar!=showProgressBar:
			self._showProgressBar=showProgressBar
			self.on_showProgressBar.emit()

	#def _setShowProgressBar

	def _getProgressBarValue(self):

		return self._progressBarValue

	#def _getProgressBarValue

	def _setProgressBarValue(self,progressBarValue):

		if self._progressBarValue!=progressBarValue:
			self._progressBarValue=progressBarValue
			self.on_progressBarValue.emit()

	def _getTotalUpdateSteps(self):

		return self._totalUpdateSteps

	#der _getTotalUpateSteps

	def _getUpdateStep(self):

		return self._updateStep

	#def _getUpdateStep

	def _setUpdateStep(self,updateStep):

		if self._updateStep!=updateStep:
			self._updateStep=updateStep
			self.on_updateStep.emit()

	#def _setUpdateStep

	def _getShowUpdateBtn(self):

		return self._showUpdateBtn

	#def _getShowUpdateBtn

	def _setShowUpdateBtn(self,showUpdateBtn):

		if self._showUpdateBtn!=showUpdateBtn:
			self._showUpdateBtn=showUpdateBtn
			self.on_showUpdateBtn.emit()

	#def _setShowUpdateBtn

	def _getEnableUpdateBtn(self):

		return self._enableUpdateBtn

	#def _getEnableUpdateBtn

	def _setEnableUpdateBtn(self,enableUpdateBtn):

		if self._enableUpdateBtn!=enableUpdateBtn:
			self._enableUpdateBtn=enableUpdateBtn
			self.on_enableUpdateBtn.emit()

	#def _setEnableUpdateBtn

	def _getShowFeedbackMessage(self):

		return self._showFeedbackMessage

	#def _getShowFeedbackMessage

	def _setShowFeedbackMessage(self,showFeedbackMessage):

		if self._showFeedbackMessage!=showFeedbackMessage:
			self._showFeedbackMessage=showFeedbackMessage
			self.on_showFeedbackMessage.emit()

	#def _setShowFeedbackMessage

	def _getUpdateRequired(self):

		return self._updateRequired

	#def _getUpdateRequired

	def _setUpdateRequired(self,updateRequired):

		if self._updateRequired!=updateRequired:
			self._updateRequired=updateRequired
			self.on_updateRequired.emit()

	#def _setUpdateRequired

	def _getCloseGui(self):

		return self._closeGui

	#def _getCloseGui	

	def _setCloseGui(self,closeGui):
		
		if self._closeGui!=closeGui:
			self._closeGui=closeGui		
			self.on_closeGui.emit()

	#def _setCloseGui

	@Slot(int)
	def manageTransitions(self,stack):

		if self.currentOptionStack!=stack:
			self.currentOptionStack=stack
			self.core.settingStack.showSettingsMsg=False

	#de manageTransitions

	@Slot()
	def openHelp(self):

		runPkexec=False

		if 'PKEXEC_UID' in os.environ:
			runPkexec=True

		self.helpCmd='xdg-open https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Lliurex+Up'

		if runPkexec:
			user=pwd.getpwuid(int(os.environ["PKEXEC_UID"])).pw_name
			self.helpCmd="su -c '%s' %s"%(self.helpCmd,user)
		else:
			self.helpCmd="su -c '%s' $USER"%self.helpCmd
		
		self.openHelp_t=threading.Thread(target=self._openHelpRet)
		self.openHelp_t.daemon=True
		self.openHelp_t.start()

	#def openHelp

	def _openHelpRet(self):

		os.system(self.helpCmd)

	#def _openHelpRet

	@Slot()
	def closeApplication(self):

		print("Cerrando")
		Bridge.llxUpConnect.cleanEnvironment()
		Bridge.llxUpConnect.cleanLliurexUpLock()
		self.closeGui=True


	#def closeApplication

	on_currentStack=Signal()
	currentStack=Property(int,_getCurrentStack,_setCurrentStack, notify=on_currentStack)
	
	on_showErrorMessage=Signal()
	showErrorMessage=Property('QVariantList',_getShowErrorMessage,_setShowErrorMessage,notify=on_showErrorMessage)

	on_currentOptionStack=Signal()
	currentOptionStack=Property(int,_getCurrentOptionStack,_setCurrentOptionStack,notify=on_currentOptionStack)

	on_showProgressBar=Signal()
	showProgressBar=Property(bool,_getShowProgessBar,_setShowProgressBar,notify=on_showProgressBar)
	
	on_progressBarValue=Signal()
	progressBarValue=Property(float,_getProgressBarValue,_setProgressBarValue,notify=on_progressBarValue)	

	on_updateStep=Signal()
	updateStep=Property(int,_getUpdateStep,_setUpdateStep,notify=on_updateStep)

	on_showUpdateBtn=Signal()
	showUpdateBtn=Property(bool,_getShowUpdateBtn,_setShowUpdateBtn,notify=on_showUpdateBtn)

	on_enableUpdateBtn=Signal()
	enableUpdateBtn=Property(bool,_getEnableUpdateBtn,_setEnableUpdateBtn,notify=on_enableUpdateBtn)

	on_showFeedbackMessage=Signal()
	showFeedbackMessage=Property('QVariantList',_getShowFeedbackMessage,_setShowFeedbackMessage,notify=on_showFeedbackMessage)	
	
	on_updateRequired=Signal()
	updateRequired=Property(bool,_getUpdateRequired,_setUpdateRequired,notify=on_updateRequired)

	on_closeGui=Signal()
	closeGui=Property(bool,_getCloseGui,_setCloseGui, notify=on_closeGui)

	totalUpdateSteps=Property(int,_getTotalUpdateSteps,constant=True)

#class Bridge

import Core

