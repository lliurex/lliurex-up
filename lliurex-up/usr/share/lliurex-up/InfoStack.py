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

class Bridge(QObject):

	versionInfoChanged = Signal()
	packagesInfoChanged = Signal()
	flatpakInfoChanged = Signal()

	def __init__(self):

		QObject.__init__(self)
		self.core = Core.Core.get_core()
		self.llxUpConnect = self.core.llxUpConnect
		self._versionInfo = {"currentVersion": None, "availableVersion": None, "candidateVersion": None}
		self._packagesInfo = {"totalPackages": 0, "upgradeSize": "", "newPackages": "", "updateSource": ""}
		self._flatpakInfo = {"totalFlatpak": 0, "size": ""}

	#def __init__

	@Property(dict, notify = versionInfoChanged)
	def versionInfo(self):

		return self._versionInfo

	#def versionInfo

	@versionInfo.setter
	def versionInfo(self,versionInfo):

		if self._versionInfo != versionInfo:
			self._versionInfo = versionInfo
			self.versionInfoChanged.emit()

	#def versionInfo

	@Property(dict, notify = packagesInfoChanged)		
	def packagesInfo(self):

		return self._packagesInfo

	#def packagesInfo

	@packagesInfo.setter
	def packagesInfo(self,packagesInfo):

		if self._packagesInfo != packagesInfo:
			self._packagesInfo = packagesInfo
			self.packagesInfoChanged.emit()

	#def packagesInfo

	@Property(dict, notify = flatpakInfoChanged)
	def flatpakInfo(self):
		
		return self._flatpakInfo
		
	#def flatpakInfo
	
	@flatpakInfo.setter
	def flatpakInfo(self,flatpakInfo):
		
		if self._flatpakInfo != flatpakInfo:
			self._flatpakInfo = flatpakInfo
			self.flatpakInfoChanged.emit()
			
	#def _setFlatpakInfo

	def getUpdateInfo(self):

		currentVersionInfo = self.core.loadStack.currentVersion

		self.versionInfo={
			"currentVersion": currentVersionInfo.get("installed"),
			"availableVersion":  self.core.loadStack.availableVersion,
			"candidateVersion": currentVersionInfo.get("candidate")
		}

		updateSource=self.core.loadStack.currentVersion["updateSource"]
		packagesInfo = self.core.loadStack.packagesInfo

		self.packagesInfo = {
			"totalPackages": packagesInfo.get("totalPackages"),
			"upgradeSize" : packagesInfo.get("upgradeSize"),
			"newPackages": self.llxUpConnect.newPackages,
			"updateSource" : currentVersionInfo.get("updateSource")
		}
		self.flatpakInfo = self.core.loadStack.flatpakInfo

	#def getUpdateInfo
		
#class Bridge

import Core

