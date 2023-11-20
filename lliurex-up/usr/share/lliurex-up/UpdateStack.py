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

class UpdateStack(QObject):

	UPDATE_PROCESS_OK=1
	UPDATE_PROCESS_ERROR=-1

	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		UpdateStack.llxUpConnect=self.core.llxUpConnect
	
	#def __init__

	def launchUpdateProcess(self):

		self._initUpdateProcess()
		self.updateProcessTimer=QTimer(None)
		self.updateProcessTimer.timeout.connect(self._updateProcessRet)
		self.updateProcessTimer.start(100)		

	#def launchedUpdateProcess

	def _initUpdateProcess(self):

		self.preActionsLaunched=False
		self.preActionsDone=False
		self.updateLaunched=False
		self.updateDone=False
		self.postActionsLaunched=False
		self.postActionsDone=False
		self.checkFinalFlavourLaunched=False
		self.checkFinalFlavourDone=False

	#def _initUpdateProcess

	def _updateProcessRet(self):

		if not self.preActionsLaunched:
			self.preActionsLaunched=True
			print("  [Lliurex-Up]: Executing pre-actions")
			self.core.mainStack.updateStep=1
			self.core.mainStack.setProgress()
			self.core.mainStack.currentCommand=UpdateStack.llxUpConnect.preActionsScript()
			self.core.mainStack.endCurrentCommand=True

		if self.preActionsDone:
			if not self.updateLaunched:
				self.updateLaunched=True
				print("  [Lliurex-Up]: Executing dist-upgrade")
				self.core.mainStack.updateStep=2
				self.core.mainStack.setProgress()
				self.core.mainStack.currentCommand=UpdateStack.llxUpConnect.distUpgradeProcess()
				self.core.mainStack.endCurrentCommand=True

			if self.updateDone:
				if not self.postActionsLaunched:
					self.postActionsLaunched=True
					print("  [Lliurex-Up]: Executing post-actions")
					self.core.mainStack.updateStep=3
					self.core.mainStack.setProgress()
					self.core.mainStack.currentCommand=UpdateStack.llxUpConnect.postActionsScript()
					self.core.mainStack.endCurrentCommand=True

				if self.postActionsDone:
					if not self.checkFinalFlavourLaunched:
						self.checkFinalFlavourLaunched=True
						print("  [Lliurex-Up]: Checking Final metapackage")
						self.core.mainStack.updateStep=4
						self.core.mainStack.setProgress()
						self.core.mainStack.currentCommand=self._checkFinalFlavour()
						self.core.mainStack.endCurrentCommand=True

					if self.checkFinalFlavourDone:
						self.updateProcessTimer.stop()	
						UpdateStack.llxUpConnect.updatePackagesData()
						self.core.packageStack.updatePackagesModelInfo()
						self.core.mainStack.showProgressBar=False
						self.core.mainStack.endProcess=True
						self.core.mainStack.updateStep=0

						if not UpdateStack.llxUpConnect.checkErrorDistUpgrade():
							self.core.mainStack.showFeedbackMessage=[True,UpdateStack.UPDATE_PROCESS_OK,"Ok"]
						else:
							self.core.mainStack.showFeedbackMessage=[True,UpdateStack.UPDATE_PROCESS_ERROR,"Error"]


		if self.preActionsLaunched:
			if not self.preActionsDone:
				if os.path.exists(UpdateStack.llxUpConnect.preactionsToken):
					self.preActionsDone=True
		
		if self.updateLaunched:
			if not self.updateDone:
				if os.path.exists(UpdateStack.llxUpConnect.upgradeToken):
					self.updateDone=True

		if self.postActionsLaunched:
			if not self.postActionsDone:
				if os.path.exists(UpdateStack.llxUpConnect.postactionsToken):
					self.postActionsDone=True

		if self.checkFinalFlavourLaunched:
			if not self.checkFinalFlavourDone:
				if os.path.exists(UpdateStack.llxUpConnect.installflavourToken):
					self.checkFinalFlavourDone=True

	#def _updateProcessRet

	def _checkFinalFlavour(self):

		flavourToInstall=UpdateStack.llxUpConnect.checkFinalFlavour()

		if len(flavourToInstall)>0:
			print("  [Lliurex-Up]: Check Final Metapackage: Instalation of metapackage is required")
			return UpdateStack.llxUpConnect.installFinalFlavour(flavourToInstall)
		else:
			print("  [Lliurex-Up]: Check Final Metapackage: Nothing to do")
			command='exit ' + '\n'
			self.checkFinalFlavourDone=True
			return command

	#def _checkFinalFlavour

#class UpdateStack

import Core

