#!/usr/bin/python3

from PySide2.QtCore import QObject,Signal,Slot,QThread,Property,QTimer,Qt,QModelIndex
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
		self._currentStack=0
		self._showErrorMessage=["","Warning"]
		self._closeGui=False

	#def __init__

	def startLliurexUp(self):

		print("iniciando")

	#def startLliurexUp

	def _getCurrentStack(self):

		return self._currentStack

	#def _getCurrentStack

	def _setCurrentStack(self,currentStack):

		if self._currentStack!=currentStack:
			self._currentStack=currentStack
			self.on_currentStack.emit()

	#def _setCurrentStack

	def _getShowErrorMessage(self):

		return self._showErrorMessage

	#def _getShowErrorMessage

	def _setShowErrorMessage(self,showErrorMessage):

		if self._showErrorMessage!=showErrorMessage:
			self._showErrorMessage=showErrorMessage
			self.on_showErrorMessage.emit()

	#def _setShowErrorMessage

	def _getCloseGui(self):

		return self._closeGui

	#def _getCloseGui	

	def _setCloseGui(self,closeGui):
		
		if self._closeGui!=closeGui:
			self._closeGui=closeGui		
			self.on_closeGui.emit()

	#def _setCloseGui

	@Slot()
	def closeApplication(self):

		self.closeGui=True

	#def closeApplication

	on_currentStack=Signal()
	currentStack=Property(int,_getCurrentStack,_setCurrentStack, notify=on_currentStack)
	
	on_showErrorMessage=Signal()
	showErrorMessage=Property('QVariantList',_getShowErrorMessage,_setShowErrorMessage,notify=on_showErrorMessage)

	on_closeGui=Signal()
	closeGui=Property(bool,_getCloseGui,_setCloseGui, notify=on_closeGui)

#class Bridge

import Core

