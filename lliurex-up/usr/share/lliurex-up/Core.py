#!/usr/bin/env python3

import sys
import lliurex.lliurexup as LliurexUpCore

import LliurexUpConnect
import MainWindow
import LoadBox
import OptionsBox
import InformationBox
import PackagesBox
import TerminalBox
import PreferencesBox
import settings

class Core:
	
	singleton=None
	DEBUG=True
	
	@classmethod
	def get_core(self):
		
		if Core.singleton==None:
			Core.singleton=Core()
			Core.singleton.init()

		return Core.singleton
		
	
	def __init__(self,args=None):
		
		self.dprint("Init...")
		
	#def __init__
	
	def init(self):

		self.rsrc_dir= settings.RSRC_DIR + "/"
		self.ui_path= settings.RSRC_DIR + "/lliurex-up.ui"
		
		self.llxUpConnect=LliurexUpConnect.LliurexUpConnect()

		self.loadBox=LoadBox.LoadBox()
		self.informationBox=InformationBox.InformationBox()
		self.packagesBox=PackagesBox.PackagesBox()
		self.terminalBox=TerminalBox.TerminalBox()
		self.preferencesBox=PreferencesBox.PreferencesBox()
		self.optionsBox=OptionsBox.OptionsBox()
		self.mainWindow=MainWindow.MainWindow()
		self.mainWindow.load_gui()
		self.mainWindow.start_gui()
			
		
		
	#def init
	
	
	
	def dprint(self,msg):
		
		if Core.DEBUG:
			
			print("[CORE] %s"%msg)
	
	#def  dprint

#class Core