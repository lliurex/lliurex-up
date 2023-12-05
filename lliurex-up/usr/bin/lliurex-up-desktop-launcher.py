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
				lock_flavour=self.get_flavour()
				if 'teachers' in user_groups:
					if 'sudo' not in user_groups and 'admins' not in user_groups:
						if lock_flavour:
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
		lock_flavour=False
		client=False
		desktop=False

		if type(result) is bytes:
			result=result.decode()
		flavours = [ x.strip() for x in result.split(',') ]	
		
		
		for item in flavours:
			if 'server' in item:
				lock_flavour=True
				break
			elif 'client' in item:
				client=True
			elif 'desktop' in item:
				desktop=True
				
		if client:
			if desktop:
				if self.check_is_connection_with_server():
					lock_flavour=True
			else:
				lock_flavour=True
							
		return lock_flavour

	#def get_flavour

	def check_is_connection_with_server(self):

		try:
			context=ssl._create_unverified_context()
			client=n4dclient.ServerProxy('https://server:9779',context=context,allow_none=True)
			test=client.is_alive('','MirrorManager')
			return True
		except Exception as e:
			return False

	#def check_is_connection_with_server
	
#def LlxUpCheckRoot

llxupCheck=LlxUpCheckRoot()		

