#!/usr/bin/python3

from PySide6.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import threading
import signal
import copy
import time
import sys
import pwd
import subprocess
import datetime


signal.signal(signal.SIGINT, signal.SIG_DFL)

class CheckSystem(QObject):

	finished = Signal(dict)

	def __init__(self,manager):

		super().__init__()
		self.manager = manager

	#def __init__

	def run (self,*args):

		ret = {
			"freeSpace":{"enoughSpace": False,"freeSpace": 0.0},
			"n4dStatus": False,
			"canConnect": False
		}

		freeSpace = self.manager.freeSpaceCheck()

		if freeSpace.get("enoughSpace"):
			n4dStatus=self.manager.checkInitialN4dStatus()
			self.manager.checkInitialFlavour()
			canConnect=self.manager.canConnectToLliurexNet()
			ret = {
				"freeSpace": freeSpace,
				"n4dStatus": n4dStatus,
				"canConnect": canConnect
			}

		self.finished.emit(ret)

	#def run

#class CheckSystem

class LaunchInitActions(QObject):

	finished = Signal(dict)

	def __init__(self,manager):

		super().__init__()
		self.manager = manager

	#def __init__

	def run (self,*args):

		ret = self.manager.initActionsScript()

		self.finished.emit(ret)
	
	#def run

#class LaunchInitActions

class CheckLliurexUp(QObject):

	finished = Signal(bool)

	def __init__(self,manager):

		super().__init__()
		self.manager = manager

	#def __init__

	def run (self,*args):
		
		ret = self.manager.isLliurexUpUpdated()
		self.finished.emit(ret)

	#def run

#class CheckLliurexUp

class UpdateLliurexUp(QObject):

	finished = Signal(dict)

	def __init__(self,manager):

		super().__init__()
		self.manager = manager

	#def __init__

	def run (self,*args):

		ret = self.manager.installLliurexUp()

		self.finished.emit(ret)
	
	#def run

#class UpdateLliurexUp

class GetCurrentVersion(QObject):

	finished = Signal(dict)

	def __init__(self,manager):

		super().__init__()
		self.manager = manager

	#def __init__

	def run (self,*args):

		ret = self.manager.getLliurexVersionLocal()

		self.finished.emit(ret)
		
	#def run

#class GetCurrentVersion

class GetAvailableVersion(QObject):

	finished = Signal(object)

	def __init__(self,manager):

		super().__init__()
		self.manager = manager
	
	#def __init__

	def run (self,*args):

		ret = self.manager.getLliurexVersionNet()

		self.finished.emit(ret)
		
	#def run

#class GetAvailableVersion

class CheckInitialFlavourToInstall(QObject):

	finished = Signal(dict)

	def __init__(self, manager):

		super().__init__()
		self.manager = manager

	#def __init__

	def run (self,*args):

		ret = {
			"status": 0,
			"data": ""
		}

		targetMetapackage = self.manager.targetMetapackage

		if not targetMetapackage:
			print("  [Lliurex-Up]: Installation of metapackage is not required")
		else:
			print("  [Lliurex-Up]: Installation of metapackage is required: " +str(targetMetapackage))
			ret = self.manager.installInitialFlavour(targetMetapackage)
	
		self.finished.emit(ret)
	
	#def run

#def CheckInitialFlavourToInstall

class GatherPackages(QObject):

	finished = Signal(dict)

	def __init__(self,manager):

		super().__init__()

		self.manager = manager
		self.packages=0
		self.updateSize=""
		self.incorrectFlavours=[]

	#def __init__

	def run (self,*args):

		packagesInfo = self.manager.getPackagesToUpdate()
		incorrectFlavours = self.manager.checkIncorrectFlavours()
		self.manager.getSystrayStatus()
		flatpakInfo = self.manager.getFlapakUpdateInfo()

		ret ={
			"packagesInfo": packagesInfo,
			"incorrectFlavours": incorrectFlavours,
			"flatpakInfo": flatpakInfo
		}

		self.finished.emit(ret)
	
	#def run

#def GatherPackages

class Bridge(QObject):

	FREESPACE_ERROR = -1
	INTERNET_CONNECTION_ERROR = -2
	UPDATE_LLIUREXUP_ERROR = -5
	SEARCH_UPDATES_ERROR = -6
	INCORRECT_METAPACKAGE_ERROR = -7
	DPKG_CONFIGURE_ERROR = -8

	loadStepChanged=Signal()
	showProgressBarChanged=Signal()
	progressValueChanged=Signal()
	countDownValueChanged=Signal()
	freeSpaceAvailableChanged=Signal()

	def __init__(self):

		QObject.__init__(self)
		self.core = Core.Core.get_core()
		self.llxUpConnect = self.core.llxUpConnect
		self._totalSteps = 9
		self._loadStep = 0
		self._showProgressBar = False
		self._progressValue = 0.0
		self._countDownValue = 5
		self.maxSeconds = 5.0
		self.currentSecond = 0.0
		self._freeSpaceAvailable = 0.00
		self._runPkexec=self.llxUpConnect.runPkexec

	#def __init__

	@Property(int, notify = loadStepChanged)
	def loadStep(self):

		return self._loadStep

	#def loadStep

	@loadStep.setter
	def loadStep(self,loadStep):

		if self._loadStep != loadStep:
			self._loadStep = loadStep
			self.loadStepChanged.emit()

	#def loadStep

	@Property(bool, notify = showProgressBarChanged)
	def showProgressBar(self):

		return self._showProgressBar

	#def _showProgressBar

	@showProgressBar.setter
	def showProgressBar(self,showProgressBar):

		if self._showProgressBar != showProgressBar:
			self._showProgressBar = showProgressBar
			self.on_showProgressBar.emit()

	#def showProgressBar

	@Property(float, notify = progressValueChanged)
	def progressValue(self):

		return self._progressValue

	#def progressValue

	@progressValue.setter
	def progressValue(self,progressValue):

		if self._progressValue != progressValue:
			self._progressValue = progressValue
			self.progressValueChanged.emit()

	#def progressValue

	@Property(int, notify = countDownValueChanged)
	def countDownValue(self):

		return self._countDownValue

	#def countDownValue

	@countDownValue.setter
	def countDownValue(self,countDownValue):

		if self._countDownValue != countDownValue:
			self._countDownValue = countDownValue
			self.countDownValueChanged.emit()

	#def countDownValue

	@Property(float, notify = freeSpaceAvailableChanged)
	def freeSpaceAvailable(self):

		return self._freeSpaceAvailable

	#def freeSpaceAvailable

	@freeSpaceAvailable.setter
	def freeSpaceAvailable(self,freeSpaceAvailable):

		if self._freeSpaceAvailable != freeSpaceAvailable:
			self._freeSpaceAvailable = freeSpaceAvailable
			self.freeSpaceAvailableChanged.emit()

	#def freeSpaceAvailable

	@Property(int, constant=True)
	def totalSteps(self):

		return self._totalSteps

	#def totalSteps

	@Property(bool,constant=True)
	def runPkexec(self):

		return self._runPkexec

	#def runPkexec

	def checkSystem(self):

		print("  [Lliurex-Up]: Checking system: connection to lliurex.gva.es, n4d status...")
		self.core.mainStack.endProcess = False
		self.loadStep = 1
		self.progressValue = self._getProgress()
		
		self.checkSystemThread = QThread()
		self.checkSystemWorker = CheckSystem(self.llxUpConnect)
		self.checkSystemWorker.moveToThread(self.checkSystemThread)

		self.checkSystemThread.started.connect(self.checkSystemWorker.run)
		self.checkSystemWorker.finished.connect(self._checkSystemRet)
		self.checkSystemWorker.finished.connect(self.checkSystemThread.quit)
		self.checkSystemWorker.finished.connect(self.checkSystemWorker.deleteLater)
		self.checkSystemThread.finished.connect(self.checkSystemThread.deleteLater)

		self.checkSystemThread.start()

	#def checkSystem

	@Slot(dict)
	def _checkSystemRet(self,ret):

		freeSpace = ret.get("freeSpace")
		n4dStatus = ret.get("n4dStatus")
		canConnect = ret.get("canConnect")

		self.freeSpaceAvailable = freeSpace.get("freeSpace")
		
		if not freeSpace.get("enoughSpace"):
			print(f"  [Lliurex-Up]: Not enough space on disk ( {self.freeSpaceAvailable} GB)")
			self.core.mainStack.showErrorMessage = {"msgCode": FREESPACE_ERROR,"type": self.llxUpConnect.KIRIGAMI_MSG_ERROR,"data":""}
			self.core.mainStack.endProcess = True
			self.core.mainStack.currentStack = 1
			return	

		if not canConnect:
			print("  [Lliurex-Up]: Unable to connect to lliurex.gva.es")
			self.core.mainStack.showErrorMessage = {"msgCode": INTERNET_CONNECTION_ERROR,"type": self.llxUpConnect.KIRIGAMI_MSG_ERROR,"data":""}
			self.core.mainStack.endProcess = True
			self.core.mainStack.currentStack = 1
			return

		self._launchInitActions()
		
	#def _checkSystemRet

	def _launchInitActions(self):

		print("  [Lliurex-Up]: Executing init-actions...")
		self.loadStep = 2
		self.progressValue = self._getProgress()
		
		self.launchInitActionsThread = QThread()
		self.launchInitActionsWorker = LaunchInitActions(self.llxUpConnect)
		self.launchInitActionsWorker.moveToThread(self.launchInitActionsThread)

		self.launchInitActionsThread.started.connect(self.launchInitActionsWorker.run)
		self.launchInitActionsWorker.finished.connect(self._checkLliurexUp)
		self.launchInitActionsWorker.finished.connect(self.launchInitActionsThread.quit)
		self.launchInitActionsWorker.finished.connect(self.launchInitActionsWorker.deleteLater)
		self.launchInitActionsThread.finished.connect(self.launchInitActionsThread.deleteLater)

		self.launchInitActionsThread.start()

	#def _launchInitActions

	@Slot(dict)
	def _checkLliurexUp(self,ret):

		self.initActionsResult = ret

		print("  [Lliurex-Up]: Checking Lliurex-Up version")
		self.loadStep = 3
		self.progressValue = self._getProgress()

		self.checkLliurexUpThread = QThread()
		self.checkLliurexUpWorker = CheckLliurexUp(self.llxUpConnect)
		self.checkLliurexUpWorker.moveToThread(self.checkLliurexUpThread)
		self.checkLliurexUpThread.started.connect(self.checkLliurexUpWorker.run)

		self.checkLliurexUpWorker.finished.connect(self._checkLliurexUpRet)
		self.checkLliurexUpWorker.finished.connect(self.checkLliurexUpThread.quit)
		self.checkLliurexUpWorker.finished.connect(self.checkLliurexUpWorker.deleteLater)
		self.checkLliurexUpThread.finished.connect(self.checkLliurexUpThread.deleteLater)

		self.checkLliurexUpThread.start()

	#def _checkLliurexUp

	@Slot(bool)
	def _checkLliurexUpRet(self,ret):

		if ret:
			self._getCurrentVersion()
		else:
			self._updateLliurexUp()

	#def _checkLliurexUpRet

	def _updateLliurexUp(self):

		print("  [Lliurex-Up]: Updating Lliurex-Up")
		self.loadStep = 4
		self.progressValue = self._getProgress()

		self.updateLliurexUpThread = QThread()
		self.updateLliurexUpWorker = UpdateLliurexUp(self.llxUpConnect)
		self.updateLliurexUpWorker.moveToThread(self.updateLliurexUpThread)
		self.updateLliurexUpThread.started.connect(self.updateLliurexUpWorker.run)

		self.updateLliurexUpWorker.finished.connect(self._updateLliurexUpRet)
		self.updateLliurexUpWorker.finished.connect(self.updateLliurexUpThread.quit)
		self.updateLliurexUpWorker.finished.connect(self.updateLliurexUpWorker.deleteLater)
		self.updateLliurexUpThread.finished.connect(self.updateLliurexUpThread.deleteLater)

		self.updateLliurexUpThread.start()

	#def _updateLliureXUp

	@Slot(dict)
	def _updateLliurexUpRet(self):

		self.core.mainStack.endProcess=True

		if not ret.get("status"):
			print("  [Lliurex-Up]: Unable to update Lliurex-Up")
			self.core.mainStack.showErrorMessage = {"msgCode": UPDATE_LLIUREXUP_ERROR,"type": self.llxUpConnect.KIRIGAMI_MSG_ERROR, "data": ret.get("data")}
			self.core.mainStack.currentStack=1
			return

		print("  [Lliurex-Up]: Reboot Lliurex-Up")
		self.loadStep = 5
		self.self.updateLliurexUpThread.wait()
		self.waitForRestartTimer = QTimer(None)
		self.waitForRestartTimer.timeout.connect(self._waitForRestartT)
		self.progressValue = 0.0
		self.waitForRestartTimer.start(10)

	#def _updateLliureXUp

	def _waitForRestartT(self):

		self.countDownValue = int(self.maxSeconds+1-self.currentSecond)
		self.progressValue = self.currentSecond/self.maxSeconds

		self.currentSecond += 0.01	
		if self.currentSecond >= self.maxSeconds:
			self.waitForRestartTimer.stop()
			self.llxUpConnect.cleanLliurexUpLock()
			os.execl(sys.executable, sys.executable, *sys.argv)

	#def _waitForRestartT

	def _getCurrentVersion(self):

		print("  [Lliurex-Up]: Looking for LliurexVersion from local repository ")
		self.loadStep = 6
		self.progressValue = self._getProgress()
		
		self.getCurrentVersionThread = QThread()
		self.getCurrentVersionWorker = GetCurrentVersion(self.llxUpConnect)
		self.getCurrentVersionWorker.moveToThread(self.getCurrentVersionThread)
		self.getCurrentVersionThread.started.connect(self.getCurrentVersionWorker.run)

		self.getCurrentVersionWorker.finished.connect(self._getAvailableVersion)
		self.getCurrentVersionWorker.finished.connect(self.getCurrentVersionThread.quit)
		self.getCurrentVersionWorker.finished.connect(self.getCurrentVersionWorker.deleteLater)
		self.getCurrentVersionThread.finished.connect(self.getCurrentVersionThread.deleteLater)

		self.getCurrentVersionThread.start()

	#def _getCurrentVersion

	@Slot(dict)
	def _getAvailableVersion(self,ret):

		self.currentVersion = ret

		print("  [Lliurex-Up]: Looking for LliurexVersion from Lliurex net")
		self.loadStep = 7
		self.progressValue=self._getProgress()

		self.getAvailableVersionThread = QThread()
		self.getAvailableVersionWorker = GetAvailableVersion(self.llxUpConnect)
		self.getAvailableVersionWorker.moveToThread(self.getAvailableVersionThread)
		self.getAvailableVersionThread.started.connect(self.getAvailableVersionWorker.run)

		self.getAvailableVersionWorker.finished.connect(self._checkInitialFlavourToInstall)
		self.getAvailableVersionWorker.finished.connect(self.getAvailableVersionThread.quit)
		self.getAvailableVersionWorker.finished.connect(self.getAvailableVersionWorker.deleteLater)
		self.getAvailableVersionThread.finished.connect(self.getAvailableVersionThread.deleteLater)

		self.getAvailableVersionThread.start()

	#def _getAvailableVersion

	@Slot(object)
	def _checkInitialFlavourToInstall(self,ret):

		self.availableVersion = ret

		print("  [Lliurex-Up]: Checking if installation of metapackage is required")
		self.loadStep = 8
		self.progressValue = self._getProgress()

		self.checkInitialFlavourToInstallThread = QThread()
		self.checkInitialFlavourToInstallWorker = CheckInitialFlavourToInstall(self.llxUpConnect)
		self.checkInitialFlavourToInstallWorker.moveToThread(self.checkInitialFlavourToInstallThread)
		self.checkInitialFlavourToInstallThread.started.connect(self.checkInitialFlavourToInstallWorker.run)

		self.checkInitialFlavourToInstallWorker.finished.connect(self._gatherPackages)
		self.checkInitialFlavourToInstallWorker.finished.connect(self.checkInitialFlavourToInstallThread.quit)
		self.checkInitialFlavourToInstallWorker.finished.connect(self.checkInitialFlavourToInstallWorker.deleteLater)
		self.checkInitialFlavourToInstallThread.finished.connect(self.checkInitialFlavourToInstallThread.deleteLater)

		self.checkInitialFlavourToInstallThread.start()


	#def _checkInitialFlavourToInstall

	@Slot(dict)
	def _gatherPackages(self,ret):

		self.isFlavourInstalled = ret

		print("  [Lliurex-Up]: Looking for for new updates")
		self.loadStep = 9
		self.progressValue = self._getProgress()

		self.gatherPackagesThread = QThread()
		self.gatherPackagesWorker = GatherPackages(self.llxUpConnect)
		self.gatherPackagesWorker.moveToThread(self.gatherPackagesThread)
		self.gatherPackagesThread.started.connect(self.gatherPackagesWorker.run)

		self.gatherPackagesWorker.finished.connect(self._gatherPackagesRet)
		self.gatherPackagesWorker.finished.connect(self.gatherPackagesThread.quit)
		self.gatherPackagesWorker.finished.connect(self.gatherPackagesWorker.deleteLater)
		self.gatherPackagesThread.finished.connect(self.gatherPackagesThread.deleteLater)

		self.gatherPackagesThread.start()


	#def _gatherPackages

	@Slot(dict)
	def _gatherPackagesRet(self,ret):

		self.core.mainStack.endProcess = True
		error = ""
		self.packagesInfo = ret.get("packagesInfo",{})
		incorrectFlavours = ret.get("incorrectFlavours",{})
		self.flatpakInfo = ret.get("flatpakInfo",{})
		
		if self.packagesInfo.get("totalPackages") == 0:
			self.core.mainStack.updateRequired = False

			if self.isFlavourInstalled.get("status") != 0:
				self.core.mainStack.updateRequired=True
				error = self.isFlavourInstalled.get("data","")
			else:	
				if self.currentVersion.get("candidate") is not None:
					if self.currentVersion.get("installed") != self.currentVersion.get("candidate"):
						self.core.mainStack.updateRequired = True
					else:
						if self.currentVersion.get("installed") != self.availableVersion:
							self.core.mainStack.updateRequired = True

			if self.core.mainStack.updateRequired:
				logMsg = "Updated aborted. An error occurred in the search for updates"
				self.llxUpConnect.log(logMsg)
				print(f"  [Lliurex-Up]: {logMsg}")
				self.core.mainStack.showErrorMessage = {"msgCode": SEARCH_UPDATES_ERROR,"type": self.llxUpConnect.KIRIGAMI_MSG_ERROR,"data":error}
				self.core.mainStack.currentStack = 1
				return
			
			logMsg="System update. Nothing to do"
			self.llxUpConnect.log(logMsg)
			
			print(f"  [Lliurex-Up]: {logMsg}")
			if not self.initActionsResult.get("status"):
				self.core.mainStack.showFeedbackMessage={"show":True,"msgCode":DPKG_CONFIGURE_ERROR,"type": self.llxUpConnect.KIRIGAMI_MSG_ERROR}
			self.core.mainStack.loadInfo()
		
		else:
			if not incorrectFlavours.get("status"):
				self.core.mainStack.updateRequired=True
				print("  [Lliurex-Up]: System not update")
				if not self.initActionsResult.get("status"):
					self.core.mainStack.showFeedbackMessage = {"show": True,"msgCode": DPKG_CONFIGURE_ERROR,"type": self.llxUpConnect.KIRIGAMI_MSG_ERROR}
				self.core.mainStack.loadInfo()
				return

			logMsg="Updated aborted for incorrect metapackages detected in update"
			self.llxUpConnect.log(logMsg)
			print(f"  [Lliurex-Up]: {logMsg}")
			self.core.mainStack.showErrorMessage = {"msgCode": INCORRECT_METAPACKAGE_ERROR,"type": self.llxUpConnect.KIRIGAMI_MSG_ERROR,"data":""}
			self.core.mainStack.currentStack=1

	#def _gatherPackagesRet

	def _getProgress(self):

		totalProgress = self.totalSteps
		currentProgress = round((self.loadStep-1)/totalProgress,1)

		return currentProgress

	#def _getProgress

		
#class Bridge

import Core

