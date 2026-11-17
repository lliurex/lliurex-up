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

	finished = Signal(str)

	def __init__(self,manager,pkgId):

		super().__init__()
		self.manager = manager
		self.pkgId = pkgId

	#def __init__

	def run(self,*args):

		ret = self.manager.getPackageChangelog(self.pkgId)

		self.finished.emit(ret)

	#def run

#class GatherChangelog

class Bridge(QObject):

	pkgChangelogChanged = Signal()

	def __init__(self):

		QObject.__init__(self)
		self.core = Core.Core.get_core()
		self.llxUpConnect = self.core.llxUpConnect
		self._packagesModel = PackagesModel.PackagesModel()
		self._pkgChangelog={"pkgId":"","changelog":""}

	#def __init__

	@Property(dict, notify = pkgChangelogChanged)
	def pkgChangelog(self):

		return self._pkgChangelog

	#def pkgChangelog

	@pkgChangelog.setter
	def pkgChangelog(self,pkgChangelog):

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

		packagesEntries = [item for item in self.llxUpConnect.packagesData if item["pkgId"] != ""]
		self._packagesModel.setEntries(packagesEntries)

	#def _updatePackagesModel

	def updatePackagesModelInfo(self):

		updatedInfo = [item for item in self.llxUpConnect.packagesData if item["pkgId"] != ""]

		for row, item in enumerate(updatedInfo):
			index = self._packagesModel.index(row)
			valuesToUpdate ={
				"pkgStatus": item["pkgStatus"],
				"showStatus": item["showStatus"]
			}

			self._packagesModel.setData(index,valuesToUpdate)

	#def updatePackagesModelInfo

	@Slot(str)
	def showPkgChangelog(self,pkgId):

		self.pkgId = pkgId
		self.pkgChangelog = {"pkgId": self.pkgId, "changelog": ""}
		
		self.gatherPkgChangelogThread = QThread()
		self.gatherPkgChangelogWorker = GatherChangelog(self.llxUpConnect,self.pkgId)
		self.gatherPkgChangelogWorker.moveToThread(self.gatherPkgChangelogThread)
		self.gatherPkgChangelogThread.started.connect(self.gatherPkgChangelogWorker.run)

		self.gatherPkgChangelogWorker.finished.connect(self._gatherPkgChangelogRet)
		self.gatherPkgChangelogWorker.finished.connect(self.gatherPkgChangelogThread.quit)
		self.gatherPkgChangelogWorker.finished.connect(self.gatherPkgChangelogWorker.deleteLater)
		self.gatherPkgChangelogThread.finished.connect(self.gatherPkgChangelogThread.deleteLater)

		self.gatherPkgChangelogThread.start()

	#def showPkgChangelog

	@Slot(str)
	def _gatherPkgChangelogRet(sel,ret):

		self.pkgChangelog={
			"pkgId": self.pkgId,
			"changelog": ret
		}

	#def _gatherPkgChangelogRet

#class Bridge

import Core

