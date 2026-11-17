#!/usr/bin/python3

from PySide6.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import signal
import copy
import time
import sys
import pwd

signal.signal(signal.SIGINT, signal.SIG_DFL)

class Bridge(QObject):

	UPDATE_NO_REQUIRED = 2

	currentStackChanged = Signal()
	showErrorMessageChanged = Signal()
	currentOptionStackChanged = Signal()
	showProgressBarChanged = Signal()
	progressBarValueChanged = Signal()
	updateStepChanged = Signal()
	showUpdateBtnChanged = Signal()
	enableUpdateBtnChanged = Signal()
	showFeedbackMessageChanged = Signal()
	updateRequiredChanged = Signal()
	endProcessChanged = Signal()
	endCurrentCommandChanged = Signal()
	endCurrentCommandChanged = Signal()
	enableKonsoleChanged = Signal()
	progressPkgChanged = Signal()
	closeGuiChanged = Signal()
	showPendingChangesDialogChanged = Signal()
	closePopUpChanged = Signal()

	def __init__(self):

		QObject.__init__(self)
		self.core = Core.Core.get_core()
		self.llxUpConnect = self.core.llxUpConnect
		self._currentStack = 0
		self._showErrorMessage = {"msgCode":"","type":"","data":""}
		self._currentOptionStack = 0
		self._showProgressBar = False
		self._progressBarValue = 0.0
		self._totalUpdateSteps = 7
		self._updateStep = 0
		self._showUpdateBtn = False
		self._enableUpdateBtn = False
		self._showFeedbackMessage = {"show":False,"msgCode":"","type":""}
		self._updateRequired = False
		self._enableKonsole = False
		self._endProcess = True
		self._endCurrentCommand = False
		self._currentCommand = ""
		self._progressPkg = 0
		self._closeGui = False
		self.moveToStack = ""
		self._showPendingChangesDialog = False
		self._closePopUp = True

	#def __init__

	@Property(int, notify = currentStackChanged)
	def currentStack(self):

		return self._currentStack

	#def currentStack

	@currentStack.setter
	def currentStack(self,currentStack):

		if self._currentStack != currentStack:
			self._currentStack = currentStack
			self.currentStackChanged.emit()

	#def currentStack

	@Property(dict, notify = showErrorMessageChanged)
	def showErrorMessage(self):

		return self._showErrorMessage

	#def showErrorMessage

	@showErrorMessage.setter
	def showErrorMessage(self,showErrorMessage):

		if self._showErrorMessage != showErrorMessage:
			self._showErrorMessage = showErrorMessage
			self.showErrorMessageChanged.emit()

	#def showErrorMessage

	@Property(int, notify = currentOptionStackChanged)
	def currentOptionStack(self):

		return self._currentOptionStack

	#def currentOptionStack

	@currentOptionStack.setter
	def currentOptionStack(self,currentOptionStack):

		if self._currentOptionStack != currentOptionStack:
			self._currentOptionStack = currentOptionStack
			self.currentOptionStackChanged.emit()

	#def currentOptionStack

	@Property(bool, notify = showProgressBarChanged)
	def showProgessBar(self):

		return self._showProgressBar

	#def showProgressBar

	@showProgessBar.setter
	def showProgressBar(self,showProgressBar):

		if self._showProgressBar != showProgressBar:
			self._showProgressBar = showProgressBar
			self.showProgressBarChanged.emit()

	#def showProgressBar

	@Property(float, notify = progressBarValueChanged)
	def progressBarValue(self):

		return self._progressBarValue

	#def progressBarValue

	@progressBarValue.setter
	def progressBarValue(self,progressBarValue):

		if self._progressBarValue != progressBarValue:
			self._progressBarValue = progressBarValue
			self.progressBarValueChanged.emit()

	#def progressBarValue

	@Property(int, notify = updateStepChanged)
	def updateStep(self):

		return self._updateStep

	#def updateStep

	@updateStep.setter
	def updateStep(self,updateStep):

		if self._updateStep != updateStep:
			self._updateStep = updateStep
			self.updateStep.emit()

	#def updateStep	

	@Property(bool, notify = showUpdateBtnChanged)
	def showUpdateBtn(self):

		return self._showUpdateBtn

	#def showUpdateBtn

	@showUpdateBtn.setter
	def showUpdateBtn(self,showUpdateBtn):

		if self._showUpdateBtn != showUpdateBtn:
			self._showUpdateBtn = showUpdateBtn
			self.showUpdateBtnChanged.emit()

	#def showUpdateBtn

	@Property(bool, notify = enableUpdateBtnChanged)
	def enableUpdateBtn(self):

		return self._enableUpdateBtn

	#def enableUpdateBtn

	@enableUpdateBtn.setter
	def enableUpdateBtn(self,enableUpdateBtn):

		if self._enableUpdateBtn != enableUpdateBtn:
			self._enableUpdateBtn = enableUpdateBtn
			self.enableUpdateBtnChanged.emit()

	#def enableUpdateBtn

	@Property(dict, notify = showFeedbackMessageChanged)	
	def showFeedbackMessage(self):

		return self._showFeedbackMessage

	#def showFeedbackMessage

	@showFeedbackMessage.setter
	def showFeedbackMessage(self,showFeedbackMessage):

		if self._showFeedbackMessage != showFeedbackMessage:
			self._showFeedbackMessage = showFeedbackMessage
			self.showFeedbackMessageChanged.emit()

	#def showFeedbackMessage

	@Property(bool, notify = updateRequiredChanged)
	def updateRequired(self):

		return self._updateRequired

	#def updateRequired

	@updateRequired.setter
	def updateRequired(self,updateRequired):

		if self._updateRequired != updateRequired:
			self._updateRequired = updateRequired
			self.updateRequiredChanged.emit()

	#def updateRequired	

	@Property(bool, notify = endProcessChanged)
	def endProcess(self):

		return self._endProcess

	#def endProcess

	@endProcess.setter
	def endProcess(self,endProcess):

		if self._endProcess != endProcess:
			self._endProcess = endProcess
			self.endProcessChanged.emit()

	#def endProcess

	@Property(bool, notify = endCurrentCommandChanged)
	def endCurrentCommand(self):

		return self._endCurrentCommand

	#def endCurrentCommand

	@endCurrentCommand.setter
	def endCurrentCommand(self,endCurrentCommand):

		if self._endCurrentCommand != endCurrentCommand:
			self._endCurrentCommand = endCurrentCommand
			self.endCurrentCommandChanged.emit()

	#def endCurrentCommand

	@Property(str, notify = endCurrentCommandChanged)
	def currentCommand(self):

		return self._currentCommand

	#def currentCommand

	@currentCommand.setter
	def currentCommand(self,currentCommand):

		if self._currentCommand != currentCommand:
			self._currentCommand = currentCommand
			self.endCurrentCommandChanged.emit()

	#def currentCommand

	@Property(bool, notify = enableKonsoleChanged)
	def enableKonsole(self):

		return self._enableKonsole

	#def enableKonsole

	@enableKonsole.setter
	def enableKonsole(self,enableKonsole):

		if self._enableKonsole != enableKonsole:
			self._enableKonsole = enableKonsole
			self.enableKonsoleChanged.emit()

	#def enableKonsole

	@Property(int, notify = progressPkgChanged)
	def progressPkg(self):

		return self._progressPkg

	#def progressPkg

	@progressPkg.setter
	def progressPkg(self,progressPkg):

		if self._progressPkg != progressPkg:
			self._progressPkg = progressPkg
			self.progressPkgChanged.emit()

	#def progressPkg

	@Property(bool, notify = closeGuiChanged)
	def closeGui(self):

		return self._closeGui

	#def closeGui	

	@closeGui.setter
	def closeGui(self,closeGui):
		
		if self._closeGui != closeGui:
			self._closeGui = closeGui		
			self.closeGuiChanged.emit()

	#def closeGui	

	@Property(bool, notify = showPendingChangesDialogChanged)
	def showPendingChangesDialog(self):

		return self._showPendingChangesDialog

	#def showPendingChangesDialog

	@showPendingChangesDialog.setter
	def showPendingChangesDialog(self,showPendingChangesDialog):

		if self._showPendingChangesDialog != showPendingChangesDialog:
			self._showPendingChangesDialog = showPendingChangesDialog
			self.showPendingChangesDialogChanged.emit()

	#def showPendingChangesDialog

	@Property(bool, notify = closePopUpChanged)
	def closePopUp(self):

		return self._closePopUp

	#def closePopUp

	@closePopUp.setter
	def closePopUp(self,closePopUp):

		if self._closePopUp != closePopUp:
			self._closePopUp = closePopUp
			self.closePopUpChanged.emit()

	#def closePopUp	

	@Property(int, constant = True)
	def totalUpdateSteps(self):

		return self._totalUpdateSteps

	#der totalUpateSteps

	def initBridge(self):

		self.llxUpConnect.startLliurexUp()
		self.core.loadStack.checkSystem()		

	#def initBridge

	def loadInfo(self):

		self.core.infoStack.getUpdateInfo()
		self.core.packageStack.getPackagesInfo()
		self.core.settingStack.getSettingsInfo()

		if self.updateRequired:
			self.showUpdateBtn = True
			self.enableUpdateBtn = True
		else:
			self.showFeedbackMessage = {"show":True,"msgCode": UPDATE_NO_REQUIRED,"type": self.llxUpConnect.KIRIGAMI_MSG_INFO}
		
		self.currentStack = 2
			
	#def loadInfo

	@Slot(int)
	def manageTransitions(self,stack):

		if self.currentOptionStack != stack:
			if self.core.settingStack.changesInSettings:
				self.moveToStack = stack
				self.showPendingChangesDialog = True
				return
			
			self.moveToStack = ""
			self.currentOptionStack = stack

			if stack == 3:
				self.core.settingStack.showSettingsMsg = {"show":False,"msgCode":"","type":""}
				self.showFeedbackMessage = {"show":False,"msgCode":"","type":""}
				return 
				
			if not self.enableKonsole and self.updateRequired and not self.enableUpdateBtn:
				self.enableUpdateBtn = True

	#de manageTransitions

	@Slot()
	def launchUpdateProcess(self):

		self.enableUpdateBtn = False
		self.showProgressBar = True
		self.endProcess = False
		self.enableKonsole = True
		self.core.updateStack.launchUpdateProcess()

	#def launchUpdateProcess

	@Slot()
	def getNewCommand(self):
		
		self.endCurrentCommand = False
		
	#def getNewCommand

	def setProgress(self):

		totalProgress = self._totalUpdateSteps
		self.progressBarValue = round((self.updateStep-1)/totalProgress,2)

	#def setProgress

	@Slot()
	def openHelp(self):

		wikiUrl = 'https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Lliurex+Up'

		realUid=os.environ.get("PKEXEC_UID") or os.environ.get("SUDO_UID")

		if realUid and os.getuid() == 0:
			cmd=["sudo","-u",f"#{realUid}","gio","open",wikiUrl]
		else:
			cmd=["xdg-open",wikiUrl]

		subprocess.Popen(cmd)

	#def openHelp
	
	@Slot(str)
	def managePendingChangesDialog(self,action):

		if action == "Apply":
			self.core.settingStack.applyChanges()			
		elif action == "Discard":
			self.core.settingStack.discardChanges()
		elif action == "Cancel":
			self.closeGui=False

		self.showPendingChangesDialog = False

	
	#def managePendingChangesDialog

	@Slot()
	def closeApplication(self):

		if not self.endProcess:
			self.closeGui = False
			return 
		
		if self.core.settingStack.changesInSettings:
			self.showPendingChangesDialog = True
			self.closeGui = False
			return

		self.llxUpConnect.cleanEnvironment()
		self.llxUpConnect.cleanLliurexUpLock()
		self.closeGui = True
		return
	
	#def closeApplication

#class Bridge

import Core

