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

	GROUPS=["admins","sudo","teachers"]
	
	def __init__(self):
		self.check_root()

	#def __init__ 	


	def check_root(self):

		user=os.environ["USER"]
		group_found=False
		run_llxup=True
		show_msg=False
		
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


		if not self.checkImageBeingEdited():				
			if group_found:		
				flavours=self.get_flavour()
				if 'teachers' in user_groups:
					if 'sudo' not in user_groups and 'admins' not in user_groups:
						if 'server' in flavours or 'client' in flavours:
							run_llxup=False

				if run_llxup:
					screensaver_inhibitor = lliurex.screensaver.InhibitScreensaver()
					screensaver_inhibitor.inHibit()
					cmd='pkexec lliurex-up'
					os.system(cmd)
					screensaver_inhibitor.unInhibit()
				else:
					show_msg=True

			else:
				show_msg=True

			if show_msg:
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

	def get_flavour(self):

		cmd='lliurex-version -v'
		p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
		result=p.communicate()[0]
		is_server=False

		if type(result) is bytes:
			result=result.decode()
		flavours = [ x.strip() for x in result.split(',') ]	
		
		'''
		for item in flavours:
			if 'server' in item:
				is_server=True
		'''					
		return flavours

	#def get_flavour
	
#def LlxUpCheckRoot

llxupCheck=LlxUpCheckRoot()		

