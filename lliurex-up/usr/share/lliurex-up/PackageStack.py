#!/usr/bin/python3

from PySide6.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import threading
import signal
import copy
import time
import sys
import pwd

import PackagesModel

signal.signal(signal.SIGINT, signal.SIG_DFL)

class GatherChangelog(QObject):

	resultReady = Signal(str,str)
	finished = Signal()

	def __init__(self, manager, pkgId):

		super().__init__()
		self.manager = manager
		self.pkgId = pkgId
		self._isCancelled = False

	#def __init__

	def cancel(self):

		self._isCancelled = True
		self.manager.cancelChangelog()

	#def cancel

	def run(self,*args):

		try:
			ret = self.manager.getPackageChangelog(self.pkgId)

			if not self._isCancelled:
				self.resultReady.emit(ret,self.pkgId)
		finally:
			self.finished.emit()

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
		self.gatherPkgChangelogWorker = None
		self.gatherPkgChangelogThread = None

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
		
		thread = QThread(self)
		worker = GatherChangelog(self.llxUpConnect,self.pkgId)

		worker.moveToThread(thread)

		thread.started.connect(worker.run)
		worker.resultReady.connect(self._gatherPkgChangelogRet)
		worker.finished.connect(thread.quit)
		worker.finished.connect(worker.deleteLater)
		#thread.finished.connect(thread.deleteLater)

		thread.finished.connect(lambda: self._clearThreadRefs(thread,worker))

		self.gatherPkgChangelogWorker = worker
		self.gatherPkgChangelogThread = thread

		thread.start()

	#def showPkgChangelog

	def _clearThreadRefs(self, thread, worker):

		if self.gatherPkgChangelogThread is thread:
			self.gatherPkgChangelogThread = None

		if self.gatherPkgChangelogWorker is worker:
			self.gatherPkgChangelogWorker = None

	#def _clearThreadRefs

	@Slot(str,str)
	def _gatherPkgChangelogRet(self,ret,pkgId):

		if pkgId == self.pkgId:
			self.pkgChangelog = {
				"pkgId": pkgId,
				"changelog": ret
			}

		self.gatherPkgChangelogWorker = None

	#def _gatherPkgChangelogRet

	@Slot()
	def stopChangelog(self):

		if self.gatherPkgChangelogWorker:
			self.gatherPkgChangelogWorker.cancel()
			try:
				self.gatherPkgChangelogWorker.resultReady.disconnect(self._gatherPkgChangelogRet)
			except RuntimeError:
				pass

		try:
			if self.gatherPkgChangelogThread and self.gatherPkgChangelogThread.isRunning():
				self.gatherPkgChangelogThread.quit()
				self.gatherPkgChangelogThread.wait(2000)
		except RuntimeError:
			pass

		self.gatherPkgChangelogWorker = None
		self.gatherPkgChangelogThread = None 
	
	#def stopChangelog

#class Bridge

import Core

