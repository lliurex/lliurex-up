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

	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		Bridge.llxUpConnect=self.core.llxUpConnect
		self._currentVersion=""
		self._availableVersion=""
		self._candidateVersion=""
		self._packagesToUpdate=0
		self._newPackagesToUpdate=0
		self._updateSize=""
		self._updateSource=""

	#def __init__

	def _getCurrentVersion(self):

		return self._currentVersion

	#def _getCurrentVersion

	def _setCurrentVersion(self,currentVersion):

		if self._currentVersion!=currentVersion:
			self._currentVersion=currentVersion
			self.on_currentVersion.emit()

	#def _setCurrentVersion

	def _getAvailableVersion(self):

		return self._availableVersion

	#def _getAvailableVersion

	def _setAvailableVersion(self,availableVersion):

		if self._availableVersion!=availableVersion:
			self._availableVersion=availableVersion
			self.on_availableVersion.emit()

	#def _setAvailableVersion

	def _getCandidateVersion(self):

		return self._candidateVersion

	#def _getCandidateVersion

	def _setCandidateVersion(self,candidateVersion):

		if self._candidateVersion!=candidateVersion:
			self._candidateVersion=candidateVersion
			self.on_candiateVersion.emit()

	#def _setCandidateVersion

	def _getPackagesToUpdate(self):

		return self._packagesToUpdate

	#def _getPackagesToUpdate

	def _setPackagesToUpdate(self,packagesToUpdate):

		if self._packagesToUpdate!=packagesToUpdate:
			self._packagesToUpdate=packagesToUpdate
			self.on_packagesToUpdate.emit()

	#def _setPackagesToUpdate

	def _getNewPackagesToUpdate(self):

		return self._newPackagesToUpdate

	#def _getNewPackagesToUpdate

	def _setNewPackagesToUpdate(self,newPackagesToUpdate):

		if self._newPackagesToUpdate!=newPackagesToUpdate:
			self._newPackagesToUpdate=newPackagesToUpdate
			self.on_newPackagesToUpdate.emit()

	#def _setNewPackagesToUpdate

	def _getUpdateSize(self):

		return self._updateSize

	#def _getUpdateSize

	def _setUpdateSize(self,updateSize):

		if self._updateSize!=updateSize:
			self._updateSize=updateSize
			self.on_updateSize.emit()

	#def _setUpdateSize

	def _getUpdateSource(self):

		return self._updateSource

	#def _getUpdateSource

	def _setUpdateSource(self,updateSource):

		if self._updateSource!=updateSource:
			self._updateSource=updateSource
			self.on_updateSource.emit()

	#def _setUpdateSource

	def getUpdateInfo(self):

		currentVersion=self.core.loadStack.getCurrentVersionT.currentVersion["installed"]
		
		if currentVersion==None:
			self.currentVersion=""
		else:
			self.currentVersion=currentVersion
		
		availableVersion=self.core.loadStack.getAvailableVersionT.availableVersion
		
		if availableVersion==None:
			if not Bridge.llxUpConnect.searchMeta('adi') and Bridge.llxUpConnect.connectionWithADI:
				self.availableVersion=="Client"
			else:
				self.availableVersion=="Connection"
		else:
			self.availableVersion=availableVersion


		candidateVersion=self.core.loadStack.getCurrentVersionT.currentVersion["candidate"]

		if candidateVersion==None:
			self.candidateVersion=""
		else:
			self.candidateVersion=candidateVersion

		if self.core.mainStack.updateRequired:
			self.packagesToUpdate=len(self.core.loadStack.gatherPackagesT.packages)
			self.newPackagesToUpdate=Bridge.llxUpConnect.newPackages
			self.updateSize=self.core.loadStack.gatherPackagesT.updateSize

		updateSource=self.core.loadStack.getCurrentVersionT.currentVersion["updateSource"]

		if updateSource==None:
			self.updateSource=""
		else:
			self.updateSource=updateSource

	#def getUpdateInfo
		

	on_currentVersion=Signal()
	currentVersion=Property(str,_getCurrentVersion,_setCurrentVersion,notify=on_currentVersion)
	
	on_availableVersion=Signal()
	availableVersion=Property(str,_getAvailableVersion,_setAvailableVersion,notify=on_availableVersion)

	on_candiateVersion=Signal()
	candidateVersion=Property(str,_getCandidateVersion,_setCandidateVersion,notify=on_candiateVersion)

	on_packagesToUpdate=Signal()
	packagesToUpdate=Property(int,_getPackagesToUpdate,_setPackagesToUpdate,notify=on_packagesToUpdate)		

	on_newPackagesToUpdate=Signal()
	newPackagesToUpdate=Property(int,_getNewPackagesToUpdate,_setNewPackagesToUpdate,notify=on_newPackagesToUpdate)

	on_updateSize=Signal()
	updateSize=Property(str,_getUpdateSize,_setUpdateSize,notify=on_updateSize)

	on_updateSource=Signal()
	updateSource=Property(str,_getUpdateSource,_setUpdateSource,notify=on_updateSource)	


#class Bridge

import Core

