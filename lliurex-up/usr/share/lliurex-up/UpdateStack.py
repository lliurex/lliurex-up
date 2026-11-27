#!/usr/bin/python3

from PySide6.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex, QMetaObject
import os
import threading
import signal
import copy
import time
import sys
import pwd


signal.signal(signal.SIGINT, signal.SIG_DFL)

class CheckProgressWorker(QObject):

	progressUpdated = Signal(dict)
	packagesModelUpdated = Signal()
	finished = Signal()

	def __init__(self, core):

		super().__init__()
		self.core = core
		self.manager = self.core.llxUpConnect
		self.aptStop = False
		self.aptRun = True
		self.unpackedRun = False
		self.installationRun = False
		self._timer = None

	#def __init__

	@Slot()
	def run(self):

		self._timer = QTimer(self)
		self._timer.timeout.connect(self._checkProgressRet)
		self._timer.start(200)
	
	#def run

	@Slot()
	def stop(self):

		if self._timer and self._timer.isActive():
			self._timer.stop()

		self.finished.emit()

	#def stop

	def _checkProgressRet(self):

		try:
			if not self.core.updateStack.updateLaunched:
				return

			totalSteps = self.core.mainStack._totalUpdateSteps
			totalPkgs = len(self.manager.initialNumberPackages)

			if not self.aptStop:
				self.manager.checkProgressDownload()
				barVal = round((1+self.manager.progressDownloadPercentage) /totalSteps,2)
				self.progressUpdated.emit({
					"progressBarValue": barVal,
					"progressPkg": self.manager.progressDownload
				})

				self.manager.checkLocks()
				self.aptRun = (self.manager.isDpkgLocked(False) == 3)

			if not self.aptRun:
				if not self.aptStop:
					self.aptStop = True
					self.unpackedRun = True
					self._timer.setInterval(1800)
				
				if self.unpackedRun:
					self.manager.checkProgressUnpacked()
					if self.manager.progressUnpacked != totalPkgs:
						barVal = round((2+self.manager.progressUnpackedPercentage) / totalSteps,2)
						self.progressUpdated.emit({
							"updateStep": 3,
							"progressBarValue": barVal,
							"progressPkg": self.manager.progressUnpacked
						})
					else:
						self.unpackedRun=False
						self.progressUpdated.emit({
							"updateStep": 3,
							"progressPkg": totalPkgs
						})
				else:
					if not self.installationRun:
						self.installationRun = True
						self.progressUpdated.emit({
							"updateStep": 4,
							"progressPkg": self.manager.progressInstallation
						})
						
					self.manager.checkProgressInstallation()
						
					if self.manager.progressInstallation != totalPkgs:
						barVal = round((3+self.manager.progressInstallationPercentage) / totalSteps,2)
						self.progressUpdated.emit({
							"updateStep": 4,
							"progressBarValue": barVal,
							"progressPkg": self.manager.progressInstallation
						})
					
					else:
						self.progressUpdated.emit({
							"progressPkg": totalPkgs
						})

						self.stop()

					self.manager.updatePackagesData()
					self.packagesModelUpdated.emit()
			
							
		except Exception as e:
			print(f"Error checking process: {e}")
			self.stop()

	#def _checkProgressRet

#class CheckProgress

class UpdateStack(QObject):

	UPDATE_PROCESS_OK = 1
	UPDATE_PROCESS_ERROR = -1

	PROCESSTOKENS=[
		("preActions", "preactionsToken"),
		("update", "upgradeToken"),
		("postActions", "postactionsToken"),
		("checkFinalFlavour", "installflavourToken"),
		("flatpakActions", "flatpakActionsToken"),
	]	

	def __init__(self):

		QObject.__init__(self)
		self.core = Core.Core.get_core()
		self.llxUpConnect = self.core.llxUpConnect
	
	#def __init__

	def launchUpdateProcess(self):

		self.core.mainStack.updateStep = 1
		self.core.mainStack.setProgress()

		self._initUpdateProcess()
		self.updateProcessTimer = QTimer(None)
		self.updateProcessTimer.timeout.connect(self._updateProcessRet)
		self.updateProcessTimer.start(1000)

		self.checkProgressThread = QThread()
		self.checkProgressWorker = CheckProgressWorker(Core.Core.get_core())
		self.checkProgressWorker.moveToThread(self.checkProgressThread)
		
		self.checkProgressThread.started.connect(self.checkProgressWorker.run)
		self.checkProgressWorker.progressUpdated.connect(self._onProgressUpdated)
		self.checkProgressWorker.packagesModelUpdated.connect(self.core.packageStack.updatePackagesModelInfo)

		self.checkProgressWorker.finished.connect(self.checkProgressThread.quit)
		self.checkProgressWorker.finished.connect(self.checkProgressWorker.deleteLater)
		self.checkProgressThread.finished.connect(self.checkProgressThread.deleteLater)

		self.checkProgressWorker.destroyed.connect(lambda: setattr(self,"checkProgressWorker",None))
		self.checkProgressThread.destroyed.connect(lambda: setattr(self,"checkProgressThread",None))

		self.checkProgressThread.start()

	#def launchedUpdateProcess

	@Slot(dict)
	def _onProgressUpdated(self,ret):

		if "updateStep" in ret:
			self.core.mainStack.updateStep = ret.get("updateStep")

		if 'progressBarValue' in ret:
			self.core.mainStack.progressBarValue = ret.get("progressBarValue")

		if 'progressPkg' in ret:
			self.core.mainStack.progressPkg = ret.get("progressPkg")
	
	#def _onProgressUpdated

	def _initUpdateProcess(self):

		self.preActionsLaunched = False
		self.preActionsDone = False
		self.updateLaunched = False
		self.updateDone = False
		self.postActionsLaunched = False
		self.postActionsDone = False
		self.checkFinalFlavourLaunched = False
		self.checkFinalFlavourDone = False
		self.flatpakActionsLaunched = False
		self.flatpakActionsDone = False

	#def _initUpdateProcess

	def _updateProcessRet(self):

		if not self.preActionsLaunched:
			self.preActionsLaunched = True
			print("  [Lliurex-Up]: Executing pre-actions")
			self.core.mainStack.setProgress()
			self.core.mainStack.currentCommand = self.llxUpConnect.preActionsScript()
			self.core.mainStack.endCurrentCommand = True

		if not self.preActionsDone:
			return self._checkProcessToken()

		if not self.updateLaunched:
			self.updateLaunched = True
			print("  [Lliurex-Up]: Executing dist-upgrade")
			self.core.mainStack.updateStep = 2
			self.core.mainStack.setProgress()
			self.core.mainStack.currentCommand = self.llxUpConnect.distUpgradeProcess()
			self.core.mainStack.endCurrentCommand = True

		if not self.updateDone:
			return self._checkProcessToken()

		if not self.postActionsLaunched:
			if getattr(self,"checkProgressWorker" ,None) is not None:
				QMetaObject.invokeMethod(
					self.checkProgressWorker,
					"stop",
					Qt.QueuedConnection
				)
			self.postActionsLaunched = True
			print("  [Lliurex-Up]: Executing post-actions")
			self.core.mainStack.updateStep = 5
			self.core.mainStack.setProgress()
			self.core.mainStack.currentCommand = self.llxUpConnect.postActionsScript()
			self.core.mainStack.endCurrentCommand = True

		if not self.postActionsDone:
			return self._checkProcessToken()

		if not self.checkFinalFlavourLaunched:
			self.checkFinalFlavourLaunched = True
			print("  [Lliurex-Up]: Checking Final metapackage")
			self.core.mainStack.updateStep = 6
			self.core.mainStack.setProgress()
			self.core.mainStack.currentCommand = self._checkFinalFlavour()
			self.core.mainStack.endCurrentCommand = True

		if not self.checkFinalFlavourDone:
			return self._checkProcessToken()

		if not self.flatpakActionsLaunched:
			self.flatpakActionsLaunched = True
			print("  [Lliurex-Up]: Updating Flatpak applications")
			self.core.mainStack.updateStep = 7
			self.core.mainStack.setProgress()
			self.core.mainStack.currentCommand = self.llxUpConnect.flatpakActionsScript()
			self.core.mainStack.endCurrentCommand = True

		if not self.flatpakActionsDone:
			return self._checkProcessToken()
						
		if self.updateProcessTimer and self.updateProcessTimer.isActive():
			self.updateProcessTimer.stop()	
	
		self.llxUpConnect.updatePackagesData(True)
		self.core.packageStack.updatePackagesModelInfo()
		self.core.mainStack.showProgressBar = False
		self.core.mainStack.endProcess = True
		self.core.mainStack.updateStep = 0

		resultProcess = self.llxUpConnect.checkErrorDistUpgrade()
		msgCode = self.UPDATE_PROCESS_OK if not resultProcess else self.UPDATE_PROCESS_ERROR
		msgType = self.llxUpConnect.KIRIGAMI_MSG_OK if not resultProcess else self.llxUpConnect.KIRIGAMI_MSG_ERROR

		self.core.mainStack.showFeedbackMessage = {"show": True, "msgCode": msgCode, "type": msgType}
	
	#def _updateProcessRet

	def _checkProcessToken(self):

		for prefix, token in self.PROCESSTOKENS:
			if getattr(self, f"{prefix}Launched") and not getattr(self, f"{prefix}Done"):
				tmpToken = getattr(self.llxUpConnect,token)
				if os.path.exists(tmpToken):
					setattr(self, f"{prefix}Done", True)

	#def _checkProcessToken

	def _checkFinalFlavour(self):

		flavourToInstall = self.llxUpConnect.checkFinalFlavour()

		if flavourToInstall:
			print("  [Lliurex-Up]: Check Final Metapackage: Instalation of metapackage is required")
			return self.llxUpConnect.installFinalFlavour(flavourToInstall)
		else:
			print("  [Lliurex-Up]: Check Final Metapackage: Nothing to do")
			command = '\n'
			self.checkFinalFlavourDone = True
			return command

	#def _checkFinalFlavour


#class UpdateStack

import Core

