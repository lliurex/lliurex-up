#!/usr/bin/python3
import os
import sys
from PySide6 import QtCore, QtGui, QtQml

class PackagesModel(QtCore.QAbstractListModel):

	PkgIdRole= QtCore.Qt.UserRole + 1000
	PkgVersionRole=QtCore.Qt.UserRole + 1001
	PkgSizeRole=QtCore.Qt.UserRole + 1002
	PkgIconRole=QtCore.Qt.UserRole + 1003
	PkgStatusRole=QtCore.Qt.UserRole + 1004
	ShowStatusRole=QtCore.Qt.UserRole + 1005


	def __init__(self,parent=None):
		
		super(PackagesModel, self).__init__(parent)
		self._entries =[]
	
	#def __init__

	def rowCount(self, parent=QtCore.QModelIndex()):
		
		if parent.isValid():
			return 0
		return len(self._entries)

	#def rowCount

	def data(self, index, role=QtCore.Qt.DisplayRole):
		
		if 0 <= index.row() < self.rowCount() and index.isValid():
			item = self._entries[index.row()]
			if role == PackagesModel.PkgIdRole:
				return item["pkgId"]
			elif role == PackagesModel.PkgVersionRole:
				return item["pkgVersion"]
			elif role == PackagesModel.PkgSizeRole:
				return item["pkgSize"]
			elif role == PackagesModel.PkgIconRole:
				return item["pkgIcon"]
			elif role == PackagesModel.PkgStatusRole:
				return item["pkgStatus"]
			elif role == PackagesModel.ShowStatusRole:
				return item["showStatus"]

		#def data

	def roleNames(self):
		
		roles = dict()
		roles[PackagesModel.PkgIdRole] = b"pkgId"
		roles[PackagesModel.PkgVersionRole] = b"pkgVersion"
		roles[PackagesModel.PkgSizeRole] = b"pkgSize"
		roles[PackagesModel.PkgIconRole] = b"pkgIcon"
		roles[PackagesModel.PkgStatusRole] = b"pkgStatus"
		roles[PackagesModel.ShowStatusRole] = b"showStatus"

		return roles

	#def roleName

	def appendRow(self,pkgid,pkgv,pkgs,pkgic,pkgst,ss):
		
		self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(),self.rowCount())
		self._entries.append(dict(pkgId=pkgid, pkgVersion=pkgv, pkgSize=pkgs, pkgIcon=pkgic, pkgStatus=pkgst, showStatus=ss))
		self.endInsertRows()

	#def appendRow

	def setData(self, index, valuesToUpdate, role=QtCore.Qt.EditRole):
		
		if role == QtCore.Qt.EditRole:
			row = index.row()
			for item in valuesToUpdate:
				for param in item:
					if param in ["pkgStatus","showStatus"]:
						if self._entries[row][param]!=item[param]:
							self._entries[row][param]=item[param]
							self.dataChanged.emit(index,index)

	#def setData

	def clear(self):
		
		count=self.rowCount()
		self.beginRemoveRows(QtCore.QModelIndex(), 0, count)
		self._entries.clear()
		self.endRemoveRows()
	
	#def clear
	
#class PackagesModel
