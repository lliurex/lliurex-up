#!/usr/bin/python3

from PySide2.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import threading
import signal
import copy
import time
import sys
import pwd
import subprocess


signal.signal(signal.SIGINT, signal.SIG_DFL)

class CheckSystem(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		self.freeSpace=False
		self.statusN4d=""
		self.canConnect=False
		self.isMirrorExistsInserver=False
		self.isMirrorRunningInserver=False

	#def __init__

	def run (self,*args):

		time.sleep(5)
		self.freeSpace=Bridge.llxUpConnect.free_space_check()
		if self.freeSpace:
			self.statusN4d=Bridge.llxUpConnect.checkInitialN4dStatus()
			Bridge.llxUpConnect.checkInitialFlavour()
			self.canConnect=Bridge.llxUpConnect.canConnectToLliurexNet()
			if self.canConnect:
				self.isMirrorExistsInserver=Bridge.llxUpConnect.clientCheckingMirrorExists()
				self.isMirrorRunningInserver=Bridge.llxUpConnect.clientCheckingMirrorIsRunning()
	#def run

#class CheckSystem

class LaunchInitActions(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		self.addRepos=args[0]
		self.addAllRepos=args[1]

	#def __init__

	def run (self,*args):

		if self.addRepos:
			Bridge.llxUpConnect.addSourcesListLliurex(self.addAllRepos)

		Bridge.llxUpConnect.initActionsScript()

	#def run

#class LaunchInitActions

class CheckLliurexUp(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		self.isLliurexUpUpdated=False

	#def __init__

	def run (self,*args):

		self.isLliurexUpUpdated=Bridge.llxUpConnect.isLliurexUpIsUpdated()

	#def run

#class CheckLliurexUp

class UpdateLliurexUp(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		self.isLliurexUpInstalled=False

	#def __init__

	def run (self,*args):
		time.sleep(5)
		self.isLliurexUpInstalled=Bridge.llxUpConnect.installLliurexUp()
	
	#def run

#class UpdateLliurexUp

class CheckMirror(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		self.isLliurexUpUpdated=False
		self.isMirrorRunning=False

	#def __init__

	def run (self,*args):

		self.isMirrorUpdate=Bridge.llxUpConnect.lliurexMirrorIsUpdated()
		self.isMirrorRunning=Bridge.llxUpConnect.lliurexMirrorIsRunning()
		
	#def run

#class CheckMirror

class LaunchMirror(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		self.ret=""

	#def __init__

	def run (self,*args):

		cmd="/usr/sbin/lliurex-mirror-gui"
		self.ret=subprocess.call(cmd,shell=True,stdout=subprocess.PIPE)
		
	#def run

#class LaunchMirror

class GetCurrentVersion(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		self.currentVersion=[]

	#def __init__

	def run (self,*args):

		self.currentVersion=Bridge.llxUpConnect.getLliurexVersionLocal()
		
	#def run

#class GetCurrentVersion

class GetAvailableVersion(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		self.availableVersion=""

	#def __init__

	def run (self,*args):

		self.availableVersion=Bridge.llxUpConnect.getLliurexVersionNet()
		
	#def run

#class GetAvailableVersion

class CheckInitialFlavourToInstall(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		self.isFlavourInstalled=0
		self.targetMetapackage=""

	#def __init__

	def run (self,*args):

		self.targetMetapackage=Bridge.llxUpConnect.targetMetapackage

		if len(self.targetMetapackage) == 0:
			print("  [Lliurex-Up]: Installation of metapackage is not required")
		else:
			print("  [Lliurex-Up]: Installation of metapackage is required: " +str(self.targetMetapackage))
			self.isFlavourInstalled=Bridge.llxUpConnect.installInitialFlavour(self.targetMetapackage)
	
	#def run

#def CheckInitialFlavourToInstall

class GatherPackages(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		self.packages=0
		self.updateSize=""
		self.incorrectFlavours=[]

	#def __init__

	def run (self,*args):

		self.packages,self.updateSize=Bridge.llxUpConnect.getPackagesToUpdate()
		self.incorrectFlavours=Bridge.llxUpConnect.checkIncorrectFlavours()
	
	#def run

#def GatherPackages

class Bridge(QObject):

	FREESPACE_ERROR=-1
	INTERNET_CONNECTION_ERROR=-2
	MIRROR_IS_RUNNING_ERROR=-3
	UNABLE_CONNECTION_TO_SERVER=-4
	UPDATE_LLIUREXUP_ERROR=-5
	SEARCH_UPDATES_ERROR=-6
	INCORRECT_METAPACKAGE_ERROR=-7


	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		Bridge.llxUpConnect=self.core.llxUpConnect
		self._totalSteps=10
		self._loadStep=0
		self._showProgressBar=False
		self._progressValue=0.0
		self._countDownValue=5
		self._mirrorPercentage=0
		self.maxSeconds=5.0
		self.currentSecond=0.0
		self._showRepoDialog=False
		self._showMirrorDialog=False
		self.addRepos=True
		self.addAllRepos=False
		self.endLaunchMirror=True

	#def __init__

	def _getTotalSteps(self):

		return self._totalSteps

	#def _getTotalSteps

	def _getLoadStep(self):

		return self._loadStep

	#def _getLoadStep

	def _setLoadStep(self,loadStep):

		if self._loadStep!=loadStep:
			self._loadStep=loadStep
			self.on_loadStep.emit()

	#def _setLoadStep

	def _getShowProgressBar(self):

		return self._showProgressBar

	#def _getShowProgressBar

	def _setShowProgressBar(self,showProgressBar):

		if self._showProgressBar!=showProgressBar:
			self._showProgressBar=showProgressBar
			self.on_showProgressBar.emit()

	#def _setShowProgressBar

	def _getProgressValue(self):

		return self._progressValue

	#def _getProgressValue

	def _setProgressValue(self,progressValue):

		if self._progressValue!=progressValue:
			self._progressValue=progressValue
			self.on_progressValue.emit()

	#def _setProgressValue

	def _getCountDownValue(self):

		return self._countDownValue

	#def _getCountDownValue

	def _setCountDownValue(self,countDownValue):

		if self._countDownValue!=countDownValue:
			self._countDownValue=countDownValue
			self.on_countDownValue.emit()

	#def _setCountDownValue

	def _getShowRepoDialog(self):

		return self._showRepoDialog

	#def _getShowRepoDialog

	def _setShowRepoDialog(self,showRepoDialog):

		if self._showRepoDialog!=showRepoDialog:
			self._showRepoDialog=showRepoDialog
			self.on_showRepoDialog.emit()

	#def _setShowRepoDialog

	def _getShowMirrorDialog(self):

		return self._showMirrorDialog

	#def _getShowRepoDialog

	def _setShowMirrorDialog(self,showMirrorDialog):

		if self._showMirrorDialog!=showMirrorDialog:
			self._showMirrorDialog=showMirrorDialog
			self.on_showMirrorDialog.emit()

	#def _setShowMirrorDialog

	def _getMirrorPercentage(self):

		return self._mirrorPercentage

	#def _getMirrorPercentage

	def _setMirrorPercentage(self,mirrorPercentage):

		if self._mirrorPercentage!=mirrorPercentage:
			self._mirrorPercentage=mirrorPercentage
			self.on_mirrorPercentage.emit()

	#def _setMirrorPercentage

	def checkSystem(self):

		print("  [Lliurex-Up]: Checking system: connection to lliurex.net, n4d status...")
		self.loadStep=1
		self.progressValue=self._getProgress()
		self.checkSystemT=CheckSystem()
		self.checkSystemT.start()
		self.checkSystemT.finished.connect(self._checkSystemRet)

	#def checkSystem

	def _checkSystemRet(self):

		abort=False

		if self.checkSystemT.freeSpace:
			if self.checkSystemT.canConnect:
				self.loadStep=2
				self.progressValue=self._getProgress()
				if not self.checkSystemT.isMirrorRunningInserver:
					if not self.checkSystemT.isMirrorExistsInserver:
						print("  [Lliurex-Up]: Asking if lliurex repository will be add to sourceslist")
						self.showRepoDialog=True
					else:
						self._launchInitActions()
				else:
					abort=True
					if self.checkSystemT.isMirrorRunningInserver:
						print("  [Lliurex-Up]: Mirror is being updated in server")
						self.core.mainStack.showErrorMessage=[Bridge.MIRROR_IS_RUNNING_ERROR,"Warning"]
					else:
						print("  [Lliurex-Up]: Unable to connect with server")
						self.core.mainStack.showErrorMessage=[Bridge.UNABLE_CONNECTION_TO_SERVER,"Error"]
			else:
				abort=True
				print("  [Lliurex-Up]: Unable to connect to lliurex.net")
				self.core.mainStack.showErrorMessage=[Bridge.INTERNET_CONNECTION_ERROR,"Error"]
				self.core.mainStack.currentStack=2
		else:
			abort=True
			print("  [Lliurex-Up]: Not enough space on disk")
			self.core.mainStack.showErrorMessage=[Bridge.FREESPACE_ERROR,"Error"]
		
		if abort:
			self.core.mainStack.currentStack=1	

	#def _checkSystemRet

	def _launchInitActions(self):

		print("  [Lliurex-Up]: Executing init-actions...")
		self.loadStep=3
		self.progressValue=self._getProgress()
		self.launchInitActionsT=LaunchInitActions(self.addRepos,self.addAllRepos)
		self.launchInitActionsT.start()
		self.launchInitActionsT.finished.connect(self._checkLliurexUp)

	#def _launchInitActions

	def _checkLliurexUp(self):

		print("  [Lliurex-Up]: Checking Lliurex-Up version")
		self.loadStep=4
		self.progressValue=self._getProgress()
		self.checkLliurexUpT=CheckLliurexUp()
		self.checkLliurexUpT.start()
		self.checkLliurexUpT.finished.connect(self._checkLliurexUpRet)

	#def _checkLliurexUp

	def _checkLliurexUpRet(self):

		if self.checkLliurexUpT.isLliurexUpUpdated:
			self._checkMirror()
		else:
			self._updateLliurexUp()

	#def _checkLliurexUpRet

	def _updateLliurexUp(self):

		print("  [Lliurex-Up]: Updating Lliurex-Up")
		self.loadStep=5
		self.progressValue=self._getProgress()
		self.updateLliurexUpT=UpdateLliurexUp()
		self.updateLliurexUpT.start()
		self.updateLliurexUpT.finished.connect(self._updateLliurexUpRet)

	#def _updateLliureXUp

	def _updateLliurexUpRet(self):

		if self.updateLliurexUpT.isLliurexUpUpdated:
			print("  [Lliurex-Up]: Reboot Lliurex-Up")
			self.loadStep=12
			self.waitForRestartTimer=QTimer(None)
			self.waitForRestartTimer.timeout.connect(self._waitForRestartT)
			self.progressValue=0.0
			self.waitForRestartTimer.start(10)
		else:
			print("  [Lliurex-Up]: Unable to update Lliurex-Up")
			self.core.mainStack.showErrorMessage=[Bridge.UPDATE_LLIUREXUP_ERROR,"Error"]
			self.core.mainStack.currentStack=1


	#def _updateLliureXUp

	def _waitForRestartT(self):

		self.countDownValue=int(self.maxSeconds+1-self.currentSecond)
		self.progressValue=self.currentSecond/self.maxSeconds

		self.currentSecond+=0.01	
		if self.currentSecond>=self.maxSeconds:
			self.waitForRestartTimer.stop()
			Bridge.llxUpConnect.cleanLliurexUpLock()
			os.execl(sys.executable, sys.executable, *sys.argv)

	#def _waitForRestartT

	def _checkMirror(self):

		print("  [Lliurex-Up]: Checking if mirror exist")
		self.loadStep=6
		self.progressValue=self._getProgress()
		self.checkMirrorT=CheckMirror()
		self.checkMirrorT.start()
		self.checkMirrorT.finished.connect(self._checkMirrorRet)

	#def _checkMirror

	def _checkMirrorRet(self):

		if not self.checkMirrorT.isMirrorUpdate:
			if not self.checkMirrorT.isMirrorRunning:
				print("  [Lliurex-Up]: Asking if mirror will be update")
				self.showMirrorDialog=True
			else:
				self._launchMirrorTimer()
		else:
			if self.checkMirrorT.isMirrorRunning:
				self._launchMirrorTimer()
			else:
				print("  [Lliurex-Up]: Nothing to do with mirror")
				self._getCurrentVersion()

	#def _checkMirrorRet

	def _launchMirror(self):

		print("  [Lliurex-Up]: Updating mirror")
		self.endLaunchMirror=False
		self._launchMirrorTimer()
		self.launchMirrorT=LaunchMirror()
		self.launchMirrorT.start()
		self.launchMirrorT.finished.connect(self._launchMirrorRet)

	#def _launchMirror

	def _launchMirrorRet(self):

		self.endLaunchMirror=True

	#def _launchMirrorRet

	def _launchMirrorTimer(self):

		self.loadStep=13
		self.progressValue=0
		self.waitForMirrorTimer=QTimer(None)
		self.waitForMirrorTimer.timeout.connect(self._waitForMirrorT)
		self.waitForMirrorTimer.start(10)

	#def _launchMirrorTimer

	def _waitForMirrorT(self):

		isMirrorRunning=Bridge.llxUpConnect.lliurexMirrorIsRunning()

		if isMirrorRunning or not self.endLaunchMirror:
			completed=Bridge.llxUpConnect.getPercentageLliurexMirror()
			self.mirrorPercentage=format(completed,'.0f')
			self.progressValue=completed/100.0
		else:
			self.waitForMirrorTimer.stop()
			self._getCurrentVersion()

	#def _waitForMirrorT

	def _getCurrentVersion(self):

		print("  [Lliurex-Up]: Looking for LliurexVersion from local repository ")
		self.loadStep=7
		self.progressValue=self._getProgress()
		self.getCurrentVersionT=GetCurrentVersion()
		self.getCurrentVersionT.start()
		self.getCurrentVersionT.finished.connect(self._getAvailableVersion)

	#def _getCurrentVersion

	def _getAvailableVersion(self):

		print("  [Lliurex-Up]: Looking for LliurexVersion from Lliurex net")
		self.loadStep=8
		self.progressValue=self._getProgress()
		self.getAvailableVersionT=GetAvailableVersion()
		self.getAvailableVersionT.start()
		self.getAvailableVersionT.finished.connect(self._checkInitialFlavourToInstall)

	#def _getAvailableVersion

	def _checkInitialFlavourToInstall(self):

		print("  [Lliurex-Up]: Checking if installation of metapackage is required")
		self.loadStep=9
		self.progressValue=self._getProgress()
		self.checkInitialFlavourToInstallT=CheckInitialFlavourToInstall()
		self.checkInitialFlavourToInstallT.start()
		self.checkInitialFlavourToInstallT.finished.connect(self._gathetPackages)

	#def _checkInitialFlavourToInstall

	def _gathetPackages(self):

		print("  [Lliurex-Up]: Looking for for new updates")
		self.loadStep=10
		self.progressValue=self._getProgress()
		self.gatherPackagesT=GatherPackages()
		self.gatherPackagesT.start()
		self.gatherPackagesT.finished.connect(self._gatherPackagesRet)

	#def _gatherPackages

	def _gatherPackagesRet(self):

		if len(self.gatherPackagesT.packages)==0:
			systemUpdate=True

			if self.checkInitialFlavourToInstallT.isFlavourInstalled!=0:
				systemUpdate=False
			else:	
				if self.getCurrentVersionT.currentVersion["candidate"]!=None:
					if self.getCurrentVersionT.currentVersion["installed"]!=self.getCurrentVersionT.currentVersion["candidate"]:
						systemUpdate=False
					else:
						if self.getCurrentVersionT.currentVersion["installed"]!=self.getAvailableVersionT.availableVersion:
							systemUpdate=False

			if not systemUpdate:
				logMsg="Updated abort. An error occurred in the search for updates"
				Bridge.llxUpConnect.log(logMsg)
				print("  [Lliurex-Up]: Error in search for updates")
				self.core.mainStack.showErrorMessage=[Bridge.SEARCH_UPDATES_ERROR,"Error"]
				self.core.mainStack.currentStack=1
			else:
				#self.core.informationStack.getUpdateSummary(True)
				logMsg="System update. Nothing to do"
				Bridge.llxUpConnect.log(logMsg)
				print("  [Lliurex-Up]: System update. Nothing to do")
				self.core.mainStack.loadInfo(True)
		else:
			if not self.gatherPackagesT.incorrectFlavours['status']:
				print("  [Lliurex-Up]: System nor update")
				self.core.mainStack.loadInfo()
			else:
				logMsg="Updated abort for incorrect metapackages detected in update"
				Bridge.llxUpConnect.log(log_msg)
				print("  [Lliurex-Up]: Update abort. Detect incorrect metapackages in new updates")
				self.core.mainStack.showErrorMessage=[Bridge.INCORRECT_METAPACKAGE_ERROR,"Error"]
				self.core.mainStack.currentStack=1

	#def _gatherPackagesRet

	def _getProgress(self):

		totalProgress=self.totalSteps+1.0
		currentProgress=round(self.loadStep/totalProgress,1)

		return currentProgress

	#def _getProgress

	@Slot(str)
	def manageRepoDialog(self,response):

		self.showRepoDialog=False
		if response=="Yes":
			self.addAllRepos=True
			logMsg="Adding the repositories of lliurex.net on client. Response: Yes"
		else:
			self.addRepos=False
			logMsg="Adding the repositories of lliurex.net on client. Response: No"
			
		Bridge.llxUpConnect.log(logMsg)
		print("  [Lliurex-Up]: "+logMsg)
		self._launchInitActions()

	#def manageRepoDialog

	@Slot(str)
	def manageMirrorDialog(self,response):

		self.showMirrorDialog=False
		if response=="Yes":
			logMsg="Update lliurex-mirror. Response: Yes"
			Bridge.llxUpConnect.log(logMsg)
			self._launchMirror()
		else:
			logMsg="Update lliurex-mirror. Response: No"
			Bridge.llxUpConnect.log(logMsg)
			self._getCurrentVersion()
			
	#def manageRepoDialog
	

	on_loadStep=Signal()
	loadStep=Property(int,_getLoadStep,_setLoadStep,notify=on_loadStep)
	
	on_showProgressBar=Signal()
	showProgressBar=Property(bool,_getShowProgressBar,_setShowProgressBar,notify=on_showProgressBar)

	on_progressValue=Signal()
	progressValue=Property(float,_getShowProgressBar,_setShowProgressBar,notify=on_showProgressBar)

	on_countDownValue=Signal()
	countDownValue=Property(int,_getCountDownValue,_setCountDownValue,notify=on_countDownValue)
	
	on_showRepoDialog=Signal()
	showRepoDialog=Property(bool,_getShowRepoDialog,_setShowRepoDialog,notify=on_showRepoDialog)

	on_showMirrorDialog=Signal()
	showMirrorDialog=Property(bool,_getShowMirrorDialog,_setShowMirrorDialog,notify=on_showMirrorDialog)

	on_mirrorPercentage=Signal()
	mirrorPercentage=Property(int,_getMirrorPercentage,_setMirrorPercentage,notify=on_mirrorPercentage)

	totalSteps=Property(int,_getTotalSteps,constant=True)

#class Bridge

import Core

