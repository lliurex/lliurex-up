#!/usr/bin/env python3


import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Pango, GdkPixbuf, Gdk, Gio, GObject,GLib,Gdk

import os
import threading
import time
import subprocess

import Core
import settings
#from . import settings
import gettext
gettext.textdomain(settings.TEXT_DOMAIN)
_ = gettext.gettext


class LoadBox(Gtk.VBox):
	
	def __init__(self):
		
		Gtk.VBox.__init__(self)
		
		self.core=Core.Core.get_core()
		
		builder=Gtk.Builder()
		builder.set_translation_domain(settings.TEXT_DOMAIN)

		ui_path=self.core.ui_path
		builder.add_from_file(ui_path)

		self.main_box=builder.get_object("load_box")
		self.load_spinner=builder.get_object("load_spinner")
		self.load_message_label=builder.get_object("load_message_label")
		self.load_pbar=builder.get_object("load_pbar")
		self.systray_label=builder.get_object("systray_label")
		self.systray_switch=builder.get_object("systray_switch")
		self.pack_start(self.main_box,True,True,0)

		self.number_process=9
		self.init_threads()

		#self.set_css_info()
		
				
	def init_threads(self):

		self.check_system_t=threading.Thread(target=self.checksystem_process)
		self.init_actions_t=threading.Thread(target=self.initactions_process)
		self.check_lliurexup_t=threading.Thread(target=self.check_lliurexup_version)
		self.install_lliurexup_t=threading.Thread(target=self.install_lliurexup)
		self.check_mirror_t=threading.Thread(target=self.check_mirror)
		self.execute_lliurexmirror_t=threading.Thread(target=self.execute_lliurexmirror)
		self.get_lliurexversionlocal_t=threading.Thread(target=self.get_lliurexversionlocal)
		self.get_lliurexversionnet_t=threading.Thread(target=self.get_lliurexversionnet)
		self.checkInitialFlavourToInstall_t=threading.Thread(target=self.checkInitialFlavourToInstall)
		self.gather_packages_t=threading.Thread(target=self.gather_packages)

		self.check_system_t.daemon=True
		self.init_actions_t.daemon=True
		self.check_lliurexup_t.daemon=True
		self.install_lliurexup_t.daemon=True
		self.check_mirror_t.daemon=True
		self.execute_lliurexmirror_t.daemon=True
		self.get_lliurexversionlocal_t.daemon=True
		self.get_lliurexversionnet_t.daemon=True
		self.checkInitialFlavourToInstall_t.daemon=True
		self.gather_packages_t.daemon=True

		self.check_system_t.done=False
		self.init_actions_t.done=False
		self.check_lliurexup_t.done=False
		self.install_lliurexup_t.done=False
		self.check_mirror_t.done=False
		self.execute_lliurexmirror_t.done=False
		self.get_lliurexversionlocal_t.done=False
		self.get_lliurexversionnet_t.done=False
		self.checkInitialFlavourToInstall_t.done=False
		self.gather_packages_t.done=False

		self.check_system_t.launched=False
		self.init_actions_t.launched=False
		self.check_lliurexup_t.launched=False
		self.install_lliurexup_t.launched=False
		self.check_mirror_t.launched=False
		self.execute_lliurexmirror_t.launched=False
		self.get_lliurexversionlocal_t.launched=False
		self.get_lliurexversionnet_t.launched=False
		self.checkInitialFlavourToInstall_t.launched=False
		self.gather_packages_t.launched=False

	#def init_threads

	def load_process(self):

		self.load_spinner.start()
		GLib.timeout_add(100,self.pulsate_checksystem)

	#def load_process()
	
	def pulsate_checksystem(self):

		abort=False
		if not self.check_system_t.launched:
			print("  [Lliurex-Up]: Checking system: connection to lliurex.net, n4d status...")
			self.check_system_t.start()
			self.check_system_t.launched=True
			self.show_number_process_executing(1,_("Checking sytem..."))
		
		if self.check_system_t.done:
			if self.free_space:
				if self.statusN4d:
					if self.can_connect:
						self.show_number_process_executing(2,_("Checking mirror..."))

						if self.is_mirror_running_inserver==False:

							if not self.is_mirror_exists_inserver:
								print("  [Lliurex-Up]: Asking if lliurex repository will be add to sourceslist")
								message=_("Mirror not detected on the server.\nDo you want to add the repositories of lliurex.net?")
								dialog = Gtk.MessageDialog(None,0,Gtk.MessageType.INFO,Gtk.ButtonsType.YES_NO,"Lliurex-Up")
								dialog.format_secondary_text(message)
								response=dialog.run()
								dialog.destroy()
								if response==Gtk.ResponseType.YES:
									log_msg="Adding the repositories of lliurex.net on client: Yes"
									print("  [Lliurex-Up]: "+log_msg)
									self.core.llxUpConnect.log(log_msg)
									self.core.llxUpConnect.addSourcesListLliurex(True)	
								else:
									log_msg="Adding the repositories of lliurex.net on client: No"
									print("  [Lliurex-Up]: "+log_msg)
									self.core.llxUpConnect.log(log_msg)
	
								GLib.timeout_add(10,self.pulsate_check_llxup_mirror)
								return False
							else:
								self.core.llxUpConnect.addSourcesListLliurex(False)
								GLib.timeout_add(10,self.pulsate_check_llxup_mirror)	
								return False

						else:
							abort=True
							if self.is_mirror_running_inserver:
								msg_gather=_("Mirror is being updated in server. Unable to update the system")
								print("  [Lliurex-Up]: Mirror is being updated in server")
							else:
								msg_gather=_("Unable to connect with server")
								print("  [Lliurex-Up]: Unable to connect with server")

					else:
						abort=True
						msg_gather=_("Unable to connect to lliurex.net")
						print("  [Lliurex-Up]: Unable to connect to lliurex.net")

				else:
					abort=True
					msg_gather=_('N4d is not working. Restart the service and try againg')
					print("  [Lliurex-Up]: N4d is not working")
			else:
				abort=True
				msg_gather=_("There's not enough space on disk to upgrade (2 GB needed)")
				print("  [Lliurex-Up]: Not enough space on disk")
								
		if abort:
			self.load_spinner.stop()
			self.load_message_label.set_markup(msg_gather)
			self.core.mainWindow.show_options(True,abort,msg_gather)
			return False
		
				
		if self.check_system_t.is_alive():
			return True		

	#def pulsate_checksystem							
	
	def checksystem_process(self):
		
		time.sleep(5)
		self.free_space=self.core.llxUpConnect.free_space_check()
		if self.free_space:
			self.statusN4d=self.core.llxUpConnect.checkInitialN4dStatus()
			if self.statusN4d:
				self.core.llxUpConnect.checkInitialFlavour()
				self.can_connect=self.core.llxUpConnect.canConnectToLliurexNet()
				if self.can_connect:
					self.is_mirror_exists_inserver=self.core.llxUpConnect.clientCheckingMirrorExists()
					self.is_mirror_running_inserver=self.core.llxUpConnect.clientCheckingMirrorIsRunning()
	
		self.check_system_t.done=True

	#def checksytem_process

	def pulsate_check_llxup_mirror(self):
		
		abort=False							

		if not self.init_actions_t.launched:
			print("  [Lliurex-Up]: Executing init-actions")
			msg_gather=_("Executing init-actions")
			self.init_actions_t.start()
			self.init_actions_t.launched=True
			self.show_number_process_executing(3,msg_gather)

		if self.init_actions_t.done:	

			if  not self.check_lliurexup_t.is_alive() and not self.check_lliurexup_t.launched:
				print("  [Lliurex-Up]: Checking Lliurex-Up version")
				msg_gather=_("Looking for new version of LliureX Up")
				self.check_lliurexup_t.start()
				self.check_lliurexup_t.launched=True
				self.show_number_process_executing(4,msg_gather)


			if  self.check_lliurexup_t.done:
				if not self.is_lliurexup_updated:
					if  not self.install_lliurexup_t.is_alive() and not self.install_lliurexup_t.launched:
						print("  [Lliurex-Up]: Updating Lliurex-Up")
						msg_gather=_("Updating LliureX Up")
						self.install_lliurexup_t.start()
						self.install_lliurexup_t.launched=True
						self.show_number_process_executing(5,msg_gather)
					else:
						if self.install_lliurexup_t.done:
							print("  [Lliurex-Up]: Reboot Lliurex-Up")
							self.msg_wait=_("LliureX Up is now updated and will be reboot in %s seconds...")
							GLib.timeout_add(10,self.wait_to_reboot)
							return False
				else:
					if not self.check_mirror_t.is_alive() and not self.check_mirror_t.launched:
						print("  [Lliurex-Up]: Checking if mirror exist")
						msg_gather=_("Checking if mirror exist and there is updated")
						self.check_mirror_t.start()
						self.check_mirror_t.launched=True
						self.show_number_process_executing(5,msg_gather)
											
					if 	self.check_mirror_t.done:
						is_mirror_running=self.core.llxUpConnect.lliurexMirrorIsRunning()
						if not self.is_mirror_updated:
							if not is_mirror_running:
								print("  [Lliurex-Up]: Asking if mirror will be update")
								message=_("Your mirror is not update. Do you want to update it?")
								dialog = Gtk.MessageDialog(None,0,Gtk.MessageType.INFO,Gtk.ButtonsType.YES_NO,"Lliurex-Up")
								dialog.format_secondary_text(message)
								response=dialog.run()
								dialog.destroy()
								if response==Gtk.ResponseType.YES:
									print("  [Lliurex-Up]: Updating mirror")
									self.updated_percentage(0)
									self.execute_lliurexmirror_t.start()
									self.mirror_running_msg()
									log_msg="Update lliurex-mirror: Yes"
									self.core.llxUpConnect.log(log_msg)
									return False
								else:
									log_msg="Update lliurex-mirror: No"
									self.core.llxUpConnect.log(log_msg)
									GLib.timeout_add(100,self.pulsate_get_info)
									return False

							else:
								self.mirror_running_msg()
								return False

						else:	
							if is_mirror_running:
								self.mirror_running_msg()
								return False
							else:	
								print("  [Lliurex-Up]: Nothing to do with mirror")
								GLib.timeout_add(100,self.pulsate_get_info)
								return False
					
							

		if self.init_actions_t.launched:
			if self.init_actions_t.is_alive():
				return True

		if  self.check_lliurexup_t.launched:
			if self.check_lliurexup_t.is_alive():
				return True

		if self.install_lliurexup_t.launched:  
			if self.install_lliurexup_t.is_alive():
				return True	
					
		if self.check_mirror_t.launched:
			if self.check_mirror_t.is_alive():
		 		return True

		
	#def pulsate_check_llxup_mirror	
	
	def initactions_process(self):

		self.core.llxUpConnect.initActionsScript()
		self.init_actions_t.done=True

	#def self.initactions_process


	def wait_to_reboot(self):

		csecond=int(self.max_seconds+1-self.current_second)
		self.load_message_label.set_text(self.msg_wait%csecond)
		self.load_pbar.set_fraction(self.current_second/self.max_seconds)

		self.current_second+=0.01

		if self.current_second>=self.max_seconds:
			self.core.llxUpConnect.cleanLliurexUpLock()
			os.execl(sys.executable, sys.executable, *sys.argv)	
			return False
		else:
			return True

	#def wait_to_reboot		

	def check_lliurexup_version(self):

		#time.sleep(5)	
		self.is_lliurexup_updated=self.core.llxUpConnect.isLliurexUpIsUpdated()
		self.check_lliurexup_t.done=True
		
	#def check_lliurexup_version	
		
	def install_lliurexup(self):

		self.is_lliurexup_installed=self.core.llxUpConnect.installLliurexUp()
		self.install_lliurexup_t.done=True

	#def install_lliurexup 	


	def check_mirror(self):

		self.is_mirror_updated=self.core.llxUpConnect.lliurexMirrorIsUpdated()
		self.check_mirror_t.done=True
	
	#def check_mirror

	def pulsate_updating_mirror(self):

		self.is_mirror_running=self.core.llxUpConnect.lliurexMirrorIsRunning()

		if self.is_mirror_running or self.execute_lliurexmirror_t.is_alive():
			mirror_percentage=self.core.llxUpConnect.getPercentageLliurexMirror()
			self.updated_percentage(mirror_percentage)
			return True
		
		else:
			GLib.timeout_add(100,self.pulsate_get_info)
			return False	

	#def pulsate_updating_mirro		

	def execute_lliurexmirror(self):
		
		#commands.getoutput('/usr/sbin/lliurex-mirror-gui')
		cmd="/usr/sbin/lliurex-mirror-gui"
		result=subprocess.call(cmd,shell=True,stdout=subprocess.PIPE)

	#def def execute_lliurexmirror	

	def mirror_running_msg(self):

		GLib.timeout_add(1000,self.pulsate_updating_mirror)

	#def mirror_running_msg	
	
	def updated_percentage(self,completed):

		percentage=completed/100.0

		self.load_pbar.set_fraction(percentage)
		
		msg_value=format(completed,'.0f')
		
		msg_percentage=_("Updating mirror: "+msg_value+"%")
		self.load_message_label.set_markup(msg_percentage)
		
		
	#def updated_percentage


	def pulsate_get_info(self):

		#self.pbar.pulse()
		if not self.get_lliurexversionlocal_t.launched:
			print("  [Lliurex-Up]: Looking for LliurexVersion from local repository ")
			msg_gather=_("Looking for new version to update")
			self.get_lliurexversionlocal_t.start()
			self.get_lliurexversionlocal_t.launched=True
			self.show_number_process_executing(6,msg_gather)


		if self.get_lliurexversionlocal_t.done:
			if not self.get_lliurexversionnet_t.is_alive() and not self.get_lliurexversionnet_t.launched:
				print("  [Lliurex-Up]: Looking for LliurexVersion from Lliurex net")
				msg_gather=_("Looking for new version available")
				self.get_lliurexversionnet_t.start()	
				self.get_lliurexversionnet_t.launched=True
				self.show_number_process_executing(7,msg_gather)


			if self.get_lliurexversionnet_t.done:

				if not self.checkInitialFlavourToInstall_t.is_alive() and not self.checkInitialFlavourToInstall_t.launched:
					print("  [Lliurex-Up]: Checking if installation of metapackage is required")
					msg_gather=_("Checking if installation of metapackage is required")
					self.checkInitialFlavourToInstall_t.start()
					self.checkInitialFlavourToInstall_t.launched=True
					self.show_number_process_executing(8,msg_gather)


				if self.checkInitialFlavourToInstall_t.done:
					if not self.gather_packages_t.is_alive() and not self.gather_packages_t.launched:
						print("  [Lliurex-Up]: Looking for for new updates")
						msg_gather=_("Looking for new updates")
						self.gather_packages_t.start()
						self.gather_packages_t.launched=True
						self.show_number_process_executing(9,msg_gather)


					if self.gather_packages_t.done:
						self.load_spinner.stop()

						if len(self.packages)==0:
								system_update=True

								if self.is_flavour_installed!=0:
									system_update=False
								else:	

									if self.version_update["candidate"]!=None:

										if self.version_update["installed"]!=self.version_update["candidate"]:
											system_update=False
															
									else:
										if self.version_update["installed"]!=self.version_available:
											system_update=False

								if not system_update:
										msg_gather=_("Updated abort. An error occurred in the search for updates")
										log_msg="Updated abort. An error occurred in the search for updates"
										self.core.llxUpConnect.log(log_msg)
										print("  [Lliurex-Up]: Error in search for updates")
										self.core.mainWindow.show_options(True,True,msg_gather)
										return False
								else:
									msg_gather=_("Your system is update")
									log_msg="System update. Nothing to do"
									self.core.llxUpConnect.log(log_msg)
									print("  [Lliurex-Up]: System update. Nothing to do")
									self.core.mainWindow.show_options(True,False,msg_gather)
									return False
													
						else:
							if not self.incorrect_flavours['status']:

								print("  [Lliurex-Up]: System nor update")
								self.core.packagesBox.draw_pkg_list()
								self.core.informationBox.get_update_summary()
								self.core.mainWindow.show_options(False,False)
								return False
							else:
								msg_gather=_("Updated abort for incorrect metapackages detected in update")+str(self.incorrect_flavours['data'])
								log_msg="Updated abort for incorrect metapackages detected in update"
								self.core.llxUpConnect.log(log_msg)
								print("  [Lliurex-Up]: Update abort. Detect incorrect metapackages in new updates")
								self.core.mainWindow.show_options(True,True,msg_gather)
							
								return False							
		

		if self.get_lliurexversionlocal_t.launched:
			if self.get_lliurexversionlocal_t.is_alive():
				return True	

		if self.get_lliurexversionnet_t.launched:
			if self.get_lliurexversionnet_t.is_alive():
				return True				

		if self.checkInitialFlavourToInstall_t.launched:
			if self.checkInitialFlavourToInstall_t.is_alive():
				return True

		if self.gather_packages_t.launched:
			if self.gather_packages_t.is_alive():
				return True

	#def pulsate_get_info	

	def get_lliurexversionlocal(self):
		self.version_update=self.core.llxUpConnect.getLliurexVersionLocal()
		self.get_lliurexversionlocal_t.done=True

	#def get_lliurexversionlocal
	
	def get_lliurexversionnet(self):
		self.version_available=self.core.llxUpConnect.getLliurexVersionNet()
		self.get_lliurexversionnet_t.done=True


	#def get_lliurexversionlocal	
	
	def checkInitialFlavourToInstall(self):
		self.is_flavour_installed=0
		self.targetMetapackage=self.core.llxUpConnect.targetMetapackage

		if len(self.targetMetapackage) == 0:
			print("  [Lliurex-Up]: Installation of metapackage is not required")
			self.checkInitialFlavourToInstall_t.done=True	

		else:
			print("  [Lliurex-Up]: Installation of metapackage is required: " +str(self.targetMetapackage))
			self.is_flavour_installed=self.core.llxUpConnect.installInitialFlavour(self.targetMetapackage)	
			self.checkInitialFlavourToInstall_t.done=True			

	#def checkInitialFlavourToInstall(
	
	def gather_packages(self):

		self.packages,self.size_update=self.core.llxUpConnect.getPackagesToUpdate()
		self.incorrect_flavours=self.core.llxUpConnect.checkIncorrectFlavours()
		self.gather_packages_t.done=True

		
	#gather_packages

	def show_number_process_executing(self, execprocess, processname):

		self.total_process=self.number_process+1.0
		self.load_pbar.set_fraction(execprocess/self.total_process)
		if processname =="":
			msg_pbar=str(execprocess) + _(" of ") + str(self.number_process)
		else:
			msg_pbar=str(execprocess) + _(" of ") + str(self.number_process)+". " + processname
	
		self.load_message_label.set_text(msg_pbar)

	#def show_number_process_executing


		
#class PreferencesBox

#from . import Core