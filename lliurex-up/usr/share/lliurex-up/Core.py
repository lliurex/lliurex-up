#!/usr/bin/env python3

import sys
import lliurex.lliurexup as LliurexUpCore

import LliurexUpConnect
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
		self.infoStack=InfoStack.Bridge()
		self.loadStack=LoadStack.Bridge()
		self.mainStack=MainStack.Bridge()
		print("Arrancando")
		self.mainStack.initBridge()
		
	#def init
	
	def dprint(self,msg):
		
		if Core.DEBUG:
			
			print("[CORE] %s"%msg)
	
	#def  dprint

#class Core