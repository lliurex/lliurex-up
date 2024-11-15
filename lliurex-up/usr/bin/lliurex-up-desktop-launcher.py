#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import sys
import grp
import pwd
import lliurex.screensaver
import xmlrpc.client as n4dclient
import ssl

import gettext
gettext.textdomain('lliurex-up')
_= gettext.gettext


class LlxUpCheckRoot():

	GROUPS=["admins","sudo","teachers"]
	
	def __init__(self):
		self.checkRoot()

	#def __init__ 	


	def checkRoot(self):

		user=os.environ["USER"]
		groupFound=False
		runLlxup=True
		showMsg=False
	
		gid = pwd.getpwnam(user).pw_gid
		groupsGids = os.getgrouplist(user, gid)
		userGroups = [ grp.getgrgid(x).gr_name for x in groupsGids ]

		for g in userGroups:
			if (g in LlxUpCheckRoot.GROUPS):
				groupFound=True

		if groupFound:		
			lockFlavour=self.get_flavour()
			if 'teachers' in userGroups:
				if 'sudo' not in userGroups and 'admins' not in userGroups:
					if lockFlavour:
						runLlxup=False

			if runLlxup:
				screensaverInhibitor = lliurex.screensaver.InhibitScreensaver()
				screensaverInhibitor.inHibit()
				cmd='pkexec lliurex-up'
				os.system(cmd)
				screensaverInhibitor.unInhibit()
			else:
				showMsg=True

		else:
			showMsg=True

		if showMsg:
				text=_("You need administration privileges to run this application.")
				cmd='kdialog --icon lliurex-up --title "Lliurex-Up" --passivepopup \
				"%s" 5'%text
				os.system(cmd)
		else:
			if 'root' in userGroups:
				cmd='lliurex-up'
				os.system(cmd)
			else:
				text=_("You need administration privileges to run this application.")
				cmd='kdialog --icon lliurex-up --title "Lliurex-Up" --passivepopup \
				"%s" 5'%text
				os.system(cmd)

	#def checkRoot

	def getFlavour(self):

		cmd='lliurex-version -v'
		p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
		result=p.communicate()[0]
		lockFlavour=False
		desktop=False

		if type(result) is bytes:
			result=result.decode()
		flavours = [ x.strip() for x in result.split(',') ]	
		
		for item in flavours:
			if 'adi' in item:
				lockFlavour=True
				break
			elif 'desktop' in item:
				desktop=True
				
		if desktop:
			if self.checkIsConnectionWithADI():
				lockFlavour=True
		else:
			lockFlavour=True
							
	#def get_flavour

	def checkIsConnectionWithADI(self):

		try:
			context=ssl._create_unverified_context()
			client=n4dclient.ServerProxy('https://server:9779',context=context,allow_none=True)
			test=client.is_alive('','MirrorManager')
			return True
		except Exception as e:
			return False

	#def checkIsConnectionWithADI
	
#def LlxUpCheckRoot

llxupCheck=LlxUpCheckRoot()		

