#!/usr/bin/python3

from PySide6.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import threading
import signal
import copy
import time
import sys
import pwd

from pathlib import Path

import LliurexUpConnect

signal.signal(signal.SIGINT, signal.SIG_DFL)

class UnlockProcess(QObject):

	finished = Signal(int)

	def __init__(self,manager):

		super().__init__()
		self.manager = manager

	#def __init__
		
	def run(self):
		
		ret = self.manager.unlockingProcess()
		self.finished.emit(ret)

	#def run

#def UnlockProcess

class Bridge(QObject):

	SERVICE_RUNNING = 1
	SOME_PROCESS_RUNNING = 2
	LOCKED_SERVICE = 3
	UNLOCK_PROCESS_RUN = 4

	NO_ADMINISTRATION_PRIVILEGES = -1
	UNLOCK_PROCESS_FAIL = -2

	isProgressBarVisibleChanged = Signal()
	dialogTextCodeChanged = Signal()
	showApplyBtnChanged=Signal()
	lockedServiceChanged=Signal()

	def __init__(self):

		QObject.__init__(self)
		self.llxUpConnnect=LliurexUpConnect.LliurexUpConnect()
		self._isProgressBarVisible = False
		self._dialogTextCode = 0
		self._showApplyBtn = False
		self._lockedService = ""
		self.abortProcess = False
		self.lockedProcess = False
		self.closeGui = True
		self._runPkexec = self.llxUpConnnect.runPkexec

	#def __init__

	@Property(bool,notify = isProgressBarVisibleChanged)
	def isProgressBarVisible(self):

		return self._isProgressBarVisible

	#def isProgressBarVisible

	@isProgressBarVisible.setter
	def isProgressBarVisible(self,isProgressBarVisible):

		if self._isProgressBarVisible != isProgressBarVisible:
			self._isProgressBarVisible = isProgressBarVisible
			self.isProgressBarVisibleChanged.emit()

	#def isProgressBarVisible

	@Property(int,notify = dialogTextCodeChanged)
	def dialogTextCode(self):

		return self._dialogTextCode

	#def dialogTextCode

	@dialogTextCode.setter
	def dialogTextCode(self,dialogTextCode):

		if self._dialogTextCode != dialogTextCode:
			self._dialogTextCode = dialogTextCode
			self.dialogTextCodeChanged.emit()

	#def dialogTextCode

	@Property(bool,notify = showApplyBtnChanged)
	def showApplyBtn(self):

		return self._showApplyBtn

	#def showApplyBtn

	@showApplyBtn.setter
	def showApplyBtn(self,showApplyBtn):

		if self._showApplyBtn != showApplyBtn:
			self._showApplyBtn = showApplyBtn
			self.showApplyBtnChanged.emit()

	#def showApplyBtn

	@Property(str,notify = lockedServiceChanged)
	def lockedService(self):

		return self._lockedService

	#def lockedService

	@lockedService.setter
	def lockedService(self,lockedService):

		if self._lockedService != lockedService:
			self._lockedService = lockedService
			self.lockedServiceChanged.emit()

	#def lockedService

	@Property(bool,constant=True)
	def runPkexec(self):

		return self._runPkexec

	#def runPkexec

	def canRunUpdate(self):

		ret = self.checkRoot()
		
		if ret:
			ret = self.getLockInfo()
		
		return ret

	#def canRunUpdate

	def checkRoot(self):

		tokenFile = Path("/etc/lliurex-up.token")

		try:
			print("  [Lliurex-Up]: Checking root")
			tokenFile.touch()
			tokenFile.unlink(missing_ok=True)
			return True
		except Exception:
			self.dialogTextCode = Bridge.NO_ADMINISTRATION_PRIVILEGES
			self.abortProcess = True
			return False
		
	#def checkRoot

	def getLockInfo(self):

		self.llxUpConnnect.checkLocks()
		
		print("  [Lliurex-Up]: Checking if LliureX-Up is running...")
		code = self.llxUpConnnect.isLliurexUpLocked()
		
		if code == 0:
			return self._isAptLocked()
		
		self.lockedService="LliureX-Up"	
		if code == 1:
			self.dialogTextCode = Bridge.SERVICE_RUNNING
			self.abortProcess = True
		elif code == 2:
			self.dialogTextCode = Bridge.LOCKED_SERVICE
			self.showApplyBtn = True
		
		return False
	
	#def _isLliurexUpLocked

	def _isAptLocked(self):

		print("  [Lliurex-Up]: Checking if Apt is running...")

		code = self.llxUpConnnect.isAptLocked()

		if code == 0:
			return self._isDpkgLocked()
		
		self.lockedService = "Apt"

		if code == 1:
			self.dialogTextCode = Bridge.SERVICE_RUNNING
			self.abortProcess = True
		elif code == 2:
			self.dialogTextCode = Bridge.LOCKED_SERVICE
			self.showApplyBtn = True
		
		return False

	#def _isAptLocked

	def _isDpkgLocked(self):

		print("  [Lliurex-Up]: Checking if Dpkg is running...")

		code = self.llxUpConnnect.isDpkgLocked()

		if code == 0:
			return True
		elif code in (1,3):
			self.lockedService = "Dpkg" if code == 1 else "Apt"	
			self.dialogTextCode = Bridge.SERVICE_RUNNING
			self.abortProcess = True
		elif code == 2:
			self.lockedService = "Dpkg"
			self.dialogTextCode = Bridge.LOCKED_SERVICE
			self.showApplyBtn = True
		
		return False
	
	#def isDpkgLocked

	@Slot()
	def launchUnlockProcess(self):

		self.dialogTextCode = Bridge.UNLOCK_PROCESS_RUN
		self.showApplyBtn = False
		self.isProgressBarVisible = True
		self.closeGui = False

		self.unlockProcessThread = QThread()
		self.unlockProcessWorker = UnlockProcess(self.llxUpConnnect)
		self.unlockProcessWorker.moveToThread(self.unlockProcessThread)

		self.unlockProcessThread.started.connect(self.unlockProcessWorker.run)
		self.unlockProcessWorker.finished.connect(self._unlockProcessRet)
		self.unlockProcessWorker.finished.connect(self.unlockProcessThread.quit)
		self.unlockProcessWorker.finished.connect(self.unlockProcessWorker.deleteLater)
		self.unlockProcessThread.finished.connect(self.unlockProcessThread.deleteLater)

		self.unlockProcessThread.start()

	#def launchUnlockProcess

	def _unlockProcessRet(self,ret):

		self.closeGui = True
		self.isProgressBarVisible = False

		if ret == 0:
			os.execl(sys.executable, sys.executable, *sys.argv) 
		else:
			self.abortProcess = True
			if ret == 1:
				self.dialogTextCode = Bridge.UNLOCK_PROCESS_FAIL
			elif ret == 2:
				self.dialogTextCode = Bridge.SOME_PROCESS_RUNNING

	#def _unlockProcessRet

	@Slot(bool,result=bool)
	def closed(self,state):
		
		return self.closeGui	

	#def closed	

#def Bridge
