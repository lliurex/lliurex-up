#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import sys
import grp
import lliurex.screensaver
import gettext
gettext.textdomain('lliurex-up')
_= gettext.gettext


class LlxUpCheckRoot():

	GROUPS=["admins","sudo"]
	
	def __init__(self):
		self.check_root()

	#def __init__ 	


	def check_root(self):

		user=os.environ["USER"]
		group_found=False
		user_groups=[]
		
		for g in grp.getgrall():
			if(g.gr_name in LlxUpCheckRoot.GROUPS):
				for member in g.gr_mem:
					if(member==user):
						group_found=True
						
			user_groups.append(g.gr_name)
						
		if not self.checkImageBeingEdited():				

			if group_found:		

				screensaver_inhibitor = lliurex.screensaver.InhibitScreensaver()
				
				screensaver_inhibitor.inHibit()
				cmd='pkexec lliurex-up'
				os.system(cmd)
				screensaver_inhibitor.unInhibit()
			else:
				text=_("You need administration privileges to run this application.")
				cmd='kdialog --icon lliurex-up --title "Lliurex-Up" --passivepopup \
				"%s" 5'%text
				os.system(cmd)
		else:
			if 'root' in user_groups:
				cmd='lliurex-up'
				os.system(cmd)
			else:
				text=_("You need administration privileges to run this application.")
				cmd='kdialog --icon lliurex-up --title "Lliurex-Up" --passivepopup \
				"%s" 5'%text
				os.system(cmd)
		
					
	#def check_root

	def checkImageBeingEdited(self):

		imageEdited=False
		if os.path.exists('/var/lib/lmd/semi'):
			if not os.path.exists('/run/lmd/semi'):
				imageEdited=True
		
		return imageEdited

	#def checkImagesBeingEdited

	
#def LlxUpCheckRoot

llxupCheck=LlxUpCheckRoot()		

