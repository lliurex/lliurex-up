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

class GatherChangelog(QThread):

	def __init__(self,*args):

		QThread.__init__(self)
		self.pkgId=args[0]
		self.ret=""

	#def __init__

	def run(self,*args):

		self.ret=Bridge.llxUpConnect.getPackageChangelog(self.pkgId)

	#def run

#class GatherChangelog

class Bridge(QObject):

	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		Bridge.llxUpConnect=self.core.llxUpConnect
		self._packagesModel=PackagesModel.PackagesModel()
		self._pkgChangelog=["",""]


	#def __init__

	def _getPackagesModel(self):

		return self._packagesModel

	#def _getCurrentVersion

	def _getPkgChangelog(self):

		return self._pkgChangelog

	#def _getPkgChangelog

	def _setPkgChangelog(self,pkgChangelog):

		if self._pkgChangelog!=pkgChangelog:
			self._pkgChangelog=pkgChangelog
			self.on_pkgChangelog.emit()

	#def _setPkgChangelog

	def getPackagesInfo(self):

		self.updatePackagesModel()

	#de getPackagesInfo

	def updatePackagesModel(self):

		ret=self._packagesModel.clear()
		packagesEntries=Bridge.llxUpConnect.packagesData
		for item in packagesEntries:
			if item["pkgId"]!="":
				self._packagesModel.appendRow(item["pkgId"],item["pkgVersion"],item["pkgSize"],item["pkgIcon"],item["pkgStatus"],item["showStatus"])

	#def _updatePackagesModel

	def updatePackagesModelInfo(self):

		params=[]
		params.append("pkgStatus")
		params.append("showStatus")

		updatedInfo=Bridge.llxUpConnect.packagesData

		if len(updatedInfo)>0:
			for i in range(len(updatedInfo)):
				valuesToUpdate=[]
				index=self._packagesModel.index(i)
				for item in params:
					tmp={}
					tmp[item]=updatedInfo[i][item]
					valuesToUpdate.append(tmp)
				self._packagesModel.setData(index,valuesToUpdate)
	
	#def updatePackagesModelInfo

	@Slot(str)
	def showPkgChangelog(self,pkgId):

		self.pkgId=pkgId
		self.pkgChangelog=[self.pkgId,""]
		self.gatherPkgChangelogT=GatherChangelog(self.pkgId)
		self.gatherPkgChangelogT.start()
		self.gatherPkgChangelogT.finished.connect(self._gatherPkgChangelogRet)

	#def showPkgChangelog

	def _gatherPkgChangelogRet(self):

		self.pkgChangelog=[self.pkgId,self.gatherPkgChangelogT.ret]

	#def _gatherPkgChangelogRet

	on_pkgChangelog=Signal()
	pkgChangelog=Property('QVariantList',_getPkgChangelog,_setPkgChangelog,notify=on_pkgChangelog)

	packagesModel=Property(QObject,_getPackagesModel,constant=True)

#class Bridge

import Core

