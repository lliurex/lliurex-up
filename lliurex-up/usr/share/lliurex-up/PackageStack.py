#!/usr/bin/python3

from PySide6.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex,QRunnable,QThreadPool
import os
import threading
import signal
import copy
import time
import sys
import pwd

import PackagesModel

signal.signal(signal.SIGINT, signal.SIG_DFL)

class WorkerSignals(QObject):

	resultReady = Signal(str,str)

#class WorkerSignals

class GatherChangelogRunnable(QRunnable):

	def __init__(self, manager, pkgId):

		super().__init__()
		self.manager = manager
		self.pkgId = pkgId
		self.signals = WorkerSignals()
		self._isCancelled = False

	#def __init__

	def cancel(self):

		self._isCancelled = True
		self.manager.cancelChangelog()

	#def cancel

	@Slot()
	def run(self,*args):

		if self._isCancelled:
			return

		ret = self.manager.getPackageChangelog(self.pkgId)

		if not self._isCancelled:
				self.signals.resultReady.emit(ret,self.pkgId)

	#def run

#class GatherChangelog

class Bridge(QObject):

	pkgChangelogChanged = Signal()

	def __init__(self):

		QObject.__init__(self)
		self.core = Core.Core.get_core()
		self.llxUpConnect = self.core.llxUpConnect
		self._packagesModel = PackagesModel.PackagesModel()
		self._pkgChangelog = {"pkgId": "", "changelog": ""}
		self.threadPool = QThreadPool.globalInstance()
		self.currentWorker = None
		self.pkgId = ""

	#def __init__

	@Property(dict, notify = pkgChangelogChanged)
	def pkgChangelog(self):

		return self._pkgChangelog

	#def pkgChangelog

	@pkgChangelog.setter
	def pkgChangelog(self, pkgChangelog):

		if self._pkgChangelog != pkgChangelog:
			self._pkgChangelog = pkgChangelog
			self.pkgChangelogChanged.emit()

	#def pkgChangelog

	@Property(QObject, constant = True)
	def packagesModel(self):

		return self._packagesModel

	#def packagesModel

	def getPackagesInfo(self):

		self.updatePackagesModel()

	#de getPackagesInfo

	def updatePackagesModel(self):

		packagesEntries = [item for item in self.llxUpConnect.packagesData if item.get("pkgId") != ""]
		self._packagesModel.setEntries(packagesEntries)

	#def _updatePackagesModel

	def updatePackagesModelInfo(self):

		updatedInfo = [item for item in self.llxUpConnect.packagesData if item.get("pkgId") != ""]

		for row, item in enumerate(updatedInfo):
			index = self._packagesModel.index(row)
			valuesToUpdate = {
				"pkgStatus": item.get("pkgStatus"),
				"showStatus": item.get("showStatus")
			}

			self._packagesModel.setData(index,valuesToUpdate)

	#def updatePackagesModelInfo

	@Slot(str)
	def showPkgChangelog(self,pkgId):

		self.stopChangelog()

		self.pkgId = pkgId
		self.pkgChangelog = {"pkgId": self.pkgId, "changelog": ""}
		
		worker = GatherChangelogRunnable(self.llxUpConnect,self.pkgId)
		worker.signals.resultReady.connect(self._gatherPkgChangelogRet)

		self.currentWorker = worker
		self.threadPool.start(worker)

		
	#def showPkgChangelog

	@Slot(str,str)
	def _gatherPkgChangelogRet(self,ret,pkgId):

		if pkgId == self.pkgId:
			self.pkgChangelog = {
				"pkgId": pkgId,
				"changelog": ret
			}

		self.currentWorker = None

	#def _gatherPkgChangelogRet

	@Slot()
	def stopChangelog(self):

		if self.currentWorker:
			self.currentWorker.cancel()
			try:
				self.currentWorker.signals.resultReady.disconnect(self._gatherPkgChangelogRet)
			except RuntimeError:
				pass

			self.currentWorker = None

	#def stopChangelog

#class Bridge

import Core

