#!/usr/bin/python3

from PySide6 import QtCore

class PackagesModel(QtCore.QAbstractListModel):

	PkgIdRole = QtCore.Qt.UserRole + 1000
	PkgVersionRole = QtCore.Qt.UserRole + 1001
	PkgSizeRole = QtCore.Qt.UserRole + 1002
	PkgIconRole = QtCore.Qt.UserRole + 1003
	PkgStatusRole = QtCore.Qt.UserRole + 1004
	ShowStatusRole = QtCore.Qt.UserRole + 1005

	_ROLE_MAP = {
		"pkgStatus" : PkgStatusRole,
		"showStatus" : ShowStatusRole
	}


	def __init__(self,parent=None):
		
		super(PackagesModel, self).__init__(parent)
		self._entries = []
	
	#def __init__

	def rowCount(self, parent=QtCore.QModelIndex()):
		
		if parent.isValid():
			return 0
		
		return len(self._entries)

	#def rowCount

	def data(self, index, role=QtCore.Qt.DisplayRole):

		if not index.isValid() or not (0 <= index.row() < self.rowCount()):
			return None

		item = self._entries[index.row()]

		if role == self.PkgIdRole:
			return item["pkgId"]
		elif role == self.PkgVersionRole:
			return item["pkgVersion"]
		elif role == self.PkgSizeRole:
			return item["pkgSize"]
		elif role == self.PkgIconRole:
			return item["pkgIcon"]
		elif role == self.PkgStatusRole:
			return item["pkgStatus"]
		elif role == self.ShowStatusRole:
			return item["showStatus"]

		return None

		#def data

	def roleNames(self):
		
		return {
			self.PkgIdRole: b"pkgId",
			self.PkgVersionRole: b"pkgVersion",
			self.PkgSizeRole: b"pkgSize",
			self.PkgIconRole: b"pkgIcon",
			self.PkgStatusRole: b"pkgStatus",
			self.ShowStatusRole: b"showStatus"
		}

	#def roleName

	def setEntries(self,entries):

		self.beginResetModel()
		self._entries = entries
		self.endResetModel()

	#de setEntries
	
	def setData(self, index, valuesToUpdate, role=QtCore.Qt.EditRole):

		if role != QtCore.Qt.EditRole or not index.isValid():
			return False
				
		row = index.row()
		if not (0 <= row < len(self._entries)):
			return False

		changeRoles = []
		for param, value in valuesToUpdate.items():
			if param in self._ROLE_MAP and self._entries[row][param] != value:
				self._entries[row][param]=value
				changeRoles.append(self._ROLE_MAP[param])

		if changeRoles:
			self.dataChanged.emit(index,index,changeRoles)
			return True

		return False

	#def setData

	def clear(self):
		
		count = self.rowCount()
		self.beginRemoveRows(QtCore.QModelIndex(), 0, count-1)
		self._entries.clear()
		self.endRemoveRows()
	
	#def clear
	
#class PackagesModel
