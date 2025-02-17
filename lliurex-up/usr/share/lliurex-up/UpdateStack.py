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

class CheckProgressWorker(QThread):


	def __init__(self,*args):

		QThread.__init__(self)
		self.core=Core.Core.get_core()
		self.llxUpConnect=self.core.llxUpConnect
		self.maxRetry=9
		self.isWorked=False
		self.aptStop=False
		self.aptRun=True
		self.unpackedRun=False
		self.installationRun=False
		self.count=0
		self.countDown=self.maxRetry
		self.isRunning=True

	#def __init__

	def run (self,*args):

		while self.isRunning:
			time.sleep(0.2)
			self._checkProgressRet()

	#def run

	def _checkProgressRet(self):

		try:
			if self.core.updateStack.updateLaunched:
				if not self.isWorked:
					self.isWorked=True
					if not self.aptStop:
						self.llxUpConnect.checkProgressDownload()
						self.core.mainStack.progressPkg=self.llxUpConnect.progressDownload
						self.core.mainStack.progressBarValue=round((1+self.llxUpConnect.progressDownloadPercentage)/self.core.mainStack._totalUpdateSteps,2)
						self.llxUpConnect.checkLocks()
						if self.llxUpConnect.isDpkgLocked()==3:
							self.aptRun=True
						else:
							self.aptRun=False

					if not self.aptRun:
						if not self.aptStop:
							self.aptStop=True
							self.unpackedRun=True

						if self.countDown==self.maxRetry:
							self.countDown=0
							if self.unpackedRun:
								self.core.mainStack.updateStep=3
								self.llxUpConnect.checkProgressUnpacked()
								if self.llxUpConnect.progressUnpacked!=len(self.llxUpConnect.initialNumberPackages):
									self.core.mainStack.progressPkg=self.llxUpConnect.progressUnpacked
									self.core.mainStack.progressBarValue=round((2+self.llxUpConnect.progressUnpackedPercentage)/self.core.mainStack._totalUpdateSteps,2)
								else:
									self.unpackedRun=False
									self.core.mainStack.progressPkg=len(self.llxUpConnect.initialNumberPackages)
							else:
								if not self.installationRun:
									self.core.mainStack.updateStep=4
									self.core.mainStack.progressPkg=self.llxUpConnect.progressInstallation
									self.installationRun=True
								self.llxUpConnect.checkProgressInstallation()
								if self.llxUpConnect.progressInstallation!=len(self.llxUpConnect.initialNumberPackages):
									self.core.mainStack.progressPkg=self.llxUpConnect.progressInstallation
									self.core.mainStack.progressBarValue=round((3+self.llxUpConnect.progressInstallationPercentage)/self.core.mainStack._totalUpdateSteps,2)
								else:
									self.core.mainStack.progressPkg=len(self.llxUpConnect.initialNumberPackages)
									self.isRunning=False
								self.llxUpConnect.updatePackagesData()
								self.core.packageStack.updatePackagesModelInfo()
						else:
							self.countDown+=1

					self.isWorked=False	
									
		except Exception as e:
			print(str(e))
			self.isRunning=False
			pass

	#def _checkProgressRet

#class CheckProgress

class UpdateStack(QObject):

	UPDATE_PROCESS_OK=1
	UPDATE_PROCESS_ERROR=-1

	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		UpdateStack.llxUpConnect=self.core.llxUpConnect
	
	#def __init__

	def launchUpdateProcess(self):

		UpdateStack.llxUpConnect.stopAutoUpgrade()
		self._initUpdateProcess()
		self.updateProcessTimer=QTimer(None)
		self.updateProcessTimer.timeout.connect(self._updateProcessRet)
		self.updateProcessTimer.start(1000)
		self.checkProgressT=CheckProgressWorker()
		self.updateProcessTimer.start(1000)
		self.checkProgressT.start()

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
					self.checkProgressT.isRunning=False
					self.postActionsLaunched=True
					print("  [Lliurex-Up]: Executing post-actions")
					self.core.mainStack.updateStep=5
					self.core.mainStack.setProgress()
					self.core.mainStack.currentCommand=UpdateStack.llxUpConnect.postActionsScript()
					self.core.mainStack.endCurrentCommand=True

				if self.postActionsDone:
					if not self.checkFinalFlavourLaunched:
						self.checkFinalFlavourLaunched=True
						print("  [Lliurex-Up]: Checking Final metapackage")
						self.core.mainStack.updateStep=6
						self.core.mainStack.setProgress()
						self.core.mainStack.currentCommand=self._checkFinalFlavour()
						self.core.mainStack.endCurrentCommand=True

					if self.checkFinalFlavourDone:
						self.updateProcessTimer.stop()	
						UpdateStack.llxUpConnect.updatePackagesData(True)
						self.core.packageStack.updatePackagesModelInfo()
						if UpdateStack.llxUpConnect.isWeekPauseActive:
							UpdateStack.llxUpConnect.getAutoUpgradeInfo()
							self.core.settingStack.getSettingsInfo()
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

