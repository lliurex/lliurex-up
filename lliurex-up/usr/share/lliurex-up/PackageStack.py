#!/usr/bin/python3

from PySide2.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
import os
import threading
import signal
import copy
import time
import sys
import pwd

import PackagesModel

signal.signal(signal.SIGINT, signal.SIG_DFL)

class Bridge(QObject):

	def __init__(self):

		QObject.__init__(self)
		self.core=Core.Core.get_core()
		Bridge.llxUpConnect=self.core.llxUpConnect
		self._packagesModel=PackagesModel.PackagesModel()
		

	#def __init__

	def _getPackagesModel(self):

		return self._packagesModel

	#def _getCurrentVersion

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


	packagesModel=Property(QObject,_getPackagesModel,constant=True)

#class Bridge

import Core

