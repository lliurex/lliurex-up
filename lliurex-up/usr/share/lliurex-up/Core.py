#!/usr/bin/env python3

import sys
import lliurex.lliurexup as LliurexUpCore

import LliurexUpConnect
import UpdateStack
import SettingStack
import PackageStack
import InfoStack
import LoadStack
import MainStack

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

		self.llxUpConnect=LliurexUpConnect.LliurexUpConnect()
		self.updateStack=UpdateStack.UpdateStack()
		self.settingStack=SettingStack.Bridge()
		self.packageStack=PackageStack.Bridge()
		self.infoStack=InfoStack.Bridge()
		self.loadStack=LoadStack.Bridge()
		self.mainStack=MainStack.Bridge()
		self.mainStack.initBridge()
		
	#def init
	
	def dprint(self,msg):
		
		if Core.DEBUG:
			
			print("[CORE] %s"%msg)
	
	#def  dprint

#class Core
