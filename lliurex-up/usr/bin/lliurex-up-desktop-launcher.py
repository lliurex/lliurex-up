#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import sys
import grp
import pwd
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
		
		#old groups method
		#for g in grp.getgrall():
		#	if(g.gr_name in LlxUpCheckRoot.GROUPS):
		#		for member in g.gr_mem:
		#			if(member==user):
		#				group_found=True

		gid = pwd.getpwnam(user).pw_gid
		groups_gids = os.getgrouplist(user, gid)
		user_groups = [ grp.getgrgid(x).gr_name for x in groups_gids ]

		for g in user_groups:
			if (g in LlxUpCheckRoot.GROUPS):
				group_found=True


						
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
					
	#def check_root
	
#def LlxUpCheckRoot

llxupCheck=LlxUpCheckRoot()		

