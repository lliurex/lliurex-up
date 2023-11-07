#!/usr/bin/python3

from PySide2.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import threading
import signal
import copy
import time
import sys
import pwd

import LliurexUpConnect

signal.signal(signal.SIGINT, signal.SIG_DFL)

class GatherLockInfo(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
	
	#def __init__
		
	def run(self,*args):
		
		Bridge.llxUpConnect.checkLocks()

	#def run

#class GatherInfo

class UnlockProcess(QThread):

	def __init__(self,*args):

		QThread.__init__(self)

	#def __init__
		
	def run(self,*args):
		
		self.ret=Bridge.llxUpConnect.unlockingProcess()

	#def run

#def UnlockProcess

class Bridge(QObject):

	SERVICE_RUNNING=1
	SOME_PROCESS_RUNNING=2
	LOCKED_SERVICE=3
	UNLOCK_PROCESS_RUN=4

	NO_ADMINISTRATION_PRIVILEGES=-1
	UNLOCK_PROCESS_FAIL=-2


	def __init__(self):

		QObject.__init__(self)
		Bridge.llxUpConnect=LliurexUpConnect.LliurexUpConnect()
		self._isProgressBarVisible=False
		self._dialogTextCode=0
		self._showApplyBtn=False
		self._lockedService=""
		self.abortProcess=False
		self.lockedProcess=False
		self.closeGui=True

	#def __init__

	def _getIsProgressBarVisible(self):

		return self._isProgressBarVisible

	#def _getIsProgressBarVisible

	def _setIsProgressBarVisible(self,isProgressBarVisible):

		if self._isProgressBarVisible!=isProgressBarVisible:
			self._isProgressBarVisible=isProgressBarVisible
			self.on_isProgressBarVisible.emit()

	#def _setIsProgressBarVisible

	def _getDialogTextCode(self):

		return self._dialogTextCode

	#def _getIsProgressBarVisible

	def _setDialogTextCode(self,dialogTextCode):

		if self._dialogTextCode!=dialogTextCode:
			self._dialogTextCode=dialogTextCode
			self.on_dialogTextCode.emit()

	#def _setDialogTextCode

	def _getShowApplyBtn(self):

		return self._showApplyBtn

	#def _getIsProgressBarVisible

	def _setShowApplyBtn(self,showApplyBtn):

		if self._showApplyBtn!=showApplyBtn:
			self._showApplyBtn=showApplyBtn
			self.on_showApplyBtn.emit()

	#def _setShowApplyBtn

	def _getLockedService(self):

		return self._lockedService

	#def _getIsProgressBarVisible

	def _setLockedService(self,lockedService):

		if self._lockedService!=lockedService:
			self._lockedService=lockedService
			self.on_lockedService.emit()

	#def _setShowApplyBtn

	def canRunUpdate(self):

		ret=self.checkRoot()
		
		if ret:
			ret=self.getLockInfo()
		
		return ret

	#def canRunUpdate

	def checkRoot(self):
		
		abort=False
		try:
			print("  [Lliurex-Up]: Checking root")
			f=open("/etc/lliurex-up.token","w")
			f.close()
			os.remove("/etc/lliurex-up.token")
			if Bridge.llxUpConnect.checkUser():
				abort=True
		except:
			abort=True
			pass
		
		if abort:
			self.dialogTextCode=Bridge.NO_ADMINISTRATION_PRIVILEGES
			self.abortProcess=True
			return False
		else:
			return True
		
	#def checkRoot

	def getLockInfo(self):

		Bridge.llxUpConnect.checkLocks()
		
		print("  [Lliurex-Up]: Checking if LliureX-Up is running...")
		code=Bridge.llxUpConnect.isLliurexUpLocked()
		
		if code==0:
			return self._isAptLocked()
		else:
			self.lockedService="LliureX-Up"	
			if code==1:
				self.dialogTextCode=Bridge.SERVICE_RUNNING
				self.abortProcess=True
				return False
			elif code==2:
				self.dialogTextCode=Bridge.LOCKED_SERVICE
				self.showApplyBtn=True
				return False
	
	#def _isLliurexUpLocked

	def _isAptLocked(self):

		print("  [Lliurex-Up]: Checking if Apt is running...")

		code=Bridge.llxUpConnect.isAptLocked()

		if code ==0:
			return self._isDpkgLocked()
		else:
			self.lockedService="Apt"	
			if code==1:
				self.dialogTextCode=Bridge.SERVICE_RUNNING
				self.abortProcess=True
				return False
			elif code==2:
				self.dialogTextCode=Bridge.LOCKED_SERVICE
				self.showApplyBtn=True
				return False

	#def _isAptLocked

	def _isDpkgLocked(self):

		print("  [Lliurex-Up]: Checking if Dpkg is running...")

		code=Bridge.llxUpConnect.isDpkgLocked()
		if code ==0:
			return True
		elif code in [1,3]:
			if code==1:
				self.lockedService="Dpkg"	
			elif code==3:
				self.lockedService="Apt"
			self.dialogTextCode=Bridge.SERVICE_RUNNING
			self.abortProcess=True
			return False
		elif code==2:
			self.dialogTextCode=Bridge.LOCKED_SERVICE
			self.showApplyBtn=True
			return False
	
	#def isDpkgLocked

	@Slot()
	def launchUnlockProcess(self):

		self.dialogTextCode=Bridge.UNLOCK_PROCESS_RUN
		self.showApplyBtn=False
		self.isProgressBarVisible=True
		self.closeGui=False
		self.unlockProcessT=UnlockProcess()
		self.unlockProcessT.start()
		self.unlockProcessT.finished.connect(self._unlockProcessRet)

	#def launchUnlockProcess

	def _unlockProcessRet(self):

		self.closeGui=True

		if self.unlockProcessT.ret==0:
			os.execl(sys.executable, sys.executable, *sys.argv) 
		else:
			self.abortProcess=True
			if self.unlockProcessT.ret==1:
				self.dialogTextCode=Bridge.UNLOCK_PROCESS_FAIL
			elif self.unlockProcessT.ret==2:
				self.dialogTextCode=Bridge.SOME_PROCESS_RUNNING

	#def _unlockProcessRet

	@Slot(bool,result=bool)
	def closed(self,state):
		
		return self.closeGui	

	#def closed	

	on_isProgressBarVisible=Signal()
	isProgressBarVisible=Property(bool,_getIsProgressBarVisible,_setIsProgressBarVisible,notify=on_isProgressBarVisible)

	on_dialogTextCode=Signal()
	dialogTextCode=Property(int,_getDialogTextCode,_setDialogTextCode,notify=on_dialogTextCode)
	
	on_showApplyBtn=Signal()
	showApplyBtn=Property(bool,_getShowApplyBtn,_setShowApplyBtn,notify=on_showApplyBtn)

	on_lockedService=Signal()
	lockedService=Property(str,_getLockedService,_setLockedService,notify=on_lockedService)

#def Bridge