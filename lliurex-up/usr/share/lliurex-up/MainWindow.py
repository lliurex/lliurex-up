#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')

import os
import shutil
import threading
import platform
import subprocess
import sys
import time
from gi.repository import Gtk, Gdk, GdkPixbuf, GObject, GLib, Gio

import Core
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

import settings
import gettext
gettext.textdomain(settings.TEXT_DOMAIN)
_ = gettext.gettext



class MainWindow:

	def __init__(self,):
		
		self.core=Core.Core.get_core()
		self.llxup_connect=self.core.llxUpConnect
		self.check_root()
		self.llxup_connect.checkLocks()
		self.isLliurexUpLocked()
			
	#def __init__		


	def isLliurexUpLocked(self):

		print("  [Lliurex-Up]: Checking if LliureX-Up is running...")

		code=self.llxup_connect.isLliurexUpLocked()

		if code !=0:
			message="Lliurex-Up"+self.getMessageDialog(code)
			self.showMessageDialog(code,message)
		else:
			self.isAptLocked()	
		
	#def islliurexup_running	


	def isAptLocked(self):

		print("  [Lliurex-Up]: Checking if Apt is running...")

		code=self.llxup_connect.isAptLocked()

		if code !=0:
			message="Apt"+self.getMessageDialog(code)
			self.showMessageDialog(code,message)
		
		else:
			self.isDpkgLocked()
	
	#def isAptLocked		


	def isDpkgLocked(self):

		print("  [Lliurex-Up]: Checking if Dpkg is running...")

		code=self.llxup_connect.isDpkgLocked()
		if code !=0:
			tmp_msg=self.getMessageDialog(code)
			if code!=3:
				message="Dpkg"+tmp_msg
			else:
				message=tmp_msg	

			self.showMessageDialog(code,message)
		else:
			self.llxup_connect.startLliurexUp()
						

	#def isDpkgLocked	


	def getMessageDialog(self,code):

		if code==1:
			msg=_(" is now running. Wait a moment and try again")
		elif code==2:
			msg=_(" seems blocked by a failed previous execution.\nLliurex-Up can not continue if this block is maintained.\nDo you want to try to unlock it? ")
		elif code==3:
			msg=_("Apt is now running. Wait a moment and try again")

		return msg

	#def getMessageDialog					

	def showMessageDialog(self,code,message):

		if code!=2:
			dialog_type=Gtk.MessageType.INFO
			dialog_buttons=Gtk.ButtonsType.OK
		else:
			dialog_type=Gtk.MessageType.WARNING
			dialog_buttons=Gtk.ButtonsType.YES_NO	

	
		dialog = Gtk.MessageDialog(None,0,dialog_type, dialog_buttons, "Lliurex-Up")
		dialog.format_secondary_text(message)
		if code!=2:
			dialog.run()
			sys.exit(1)
		else:
			response=dialog.run()
			dialog.destroy()
			if response==Gtk.ResponseType.YES:
				GObject.threads_init()
				self.unlocking_t=threading.Thread(target=self.unlocking_process)
				self.unlocking_t.daemon=True
				self.unlocking_t.launched=False
				self.unlocking_t.done=False
				GLib.timeout_add(100,self.pulsate_unlocking_process)
				self.showProgressDialog()
				

			else:
				sys.exit(1)		
		
					
	#def showMessageDialog				

	def showProgressDialog(self):

		self.unlocking_dialog = Gtk.MessageDialog(None,0,Gtk.MessageType.INFO, Gtk.ButtonsType.CANCEL, "Lliurex-Up")
		self.unlocking_dialog.set_size_request(510, 40)
		self.unlocking_dialog.format_secondary_text(_("The unlocking process is running. Wait a moment..."))
		self.unlocking_dialog_pbar=Gtk.ProgressBar()
		self.unlocking_dialog_pbar.set_margin_left(15)
		self.unlocking_dialog_pbar.set_margin_right(15)

		self.unlocking_dialog_pbar.show()
		
		self.unlocking_dialog.get_children()[0].pack_start(self.unlocking_dialog_pbar,False,False,20)
		self.unlocking_dialog.get_children()[0].get_children()[2].hide()
		self.unlocking_dialog.run()

	#def showProgressDialog	


	def pulsate_unlocking_process(self):


		if not self.unlocking_t.launched:
			self.unlocking_t.launched=True
			self.unlocking_t.start()
			

		if self.unlocking_t.done:
			self.unlocking_dialog.destroy()	
			if self.result_unlocking !=0:
				if self.result_unlocking==1:
					dialog_type=Gtk.MessageType.ERROR
					message=_("The unlocking process has failed")
				else:
					dialog_type=Gtk.MessageType.INFO
					message=_("Some process are running. Wait a moment and try again")	
					
				dialog=Gtk.MessageDialog(None,0,dialog_type, Gtk.ButtonsType.CANCEL, "Lliurex-Up")
				dialog.format_secondary_text(message)
				dialog.run()
				sys.exit(1)
			else:		
				os.execl(sys.executable, sys.executable, *sys.argv)	

		if self.unlocking_t.launched:
			if not self.unlocking_t.done:
				self.unlocking_dialog_pbar.pulse()
				return True		


	#def pulsate_unlocking_process	


	def unlocking_process(self):

		self.result_unlocking=self.llxup_connect.unlockingProcess()
		self.unlocking_t.done=True

	#def unlocking_process

	def check_root(self):
		
		try:
			print("  [Lliurex-Up]: Checking root")
			f=open("/etc/lliurex-up.token","w")
			f.close()
			os.remove("/etc/lliurex-up.token")

		except:
			print("  [Lliurex-Up]: No administration privileges")
			dialog = Gtk.MessageDialog(None,0,Gtk.MessageType.ERROR, Gtk.ButtonsType.CANCEL, "Lliurex-Up")
			dialog.format_secondary_text(_("You need administration privileges to run this application."))
			dialog.run()
			sys.exit(1)
		
	#def check_root

	def load_gui(self):
		
		builder=Gtk.Builder()
		builder.set_translation_domain(settings.TEXT_DOMAIN)
		ui_path=self.core.ui_path
		builder.add_from_file(ui_path)

		self.css_file=self.core.rsrc_dir+"lliurex-up.css"

		self.stack = Gtk.Stack()
		self.stack.set_transition_duration(1000)
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)


		self.main_window=builder.get_object("main_window")
		self.main_window.set_title("Lliurex-Up")
		self.main_window.resize(835,610)
		self.banner_box=builder.get_object("banner_box")
		self.window_box=builder.get_object("window_box")
		self.main_box=builder.get_object("main_box")
		self.bottom_box=builder.get_object("bottom_box")
		self.progress_label_box=builder.get_object("progress_label_box")
		self.progress_label_ok_img=builder.get_object("pl_ok_img")
		self.progress_label_error_img=builder.get_object("pl_error_img")
		self.progress_label=builder.get_object("progress_label")
		self.progress_bar_box=builder.get_object("pb_box")
		self.progress_bar=builder.get_object("progress_bar")
		self.update_btn=builder.get_object("update_btn")
		
		self.loadBox=self.core.loadBox
		self.optionsBox=self.core.optionsBox

		self.stack.add_titled(self.loadBox,"load","Load")
		self.stack.add_titled(self.optionsBox,"options", "Options")

		self.main_box.pack_start(self.stack,False,False,0)

		self.main_window.show_all()
		
		self.progress_label_ok_img.hide()
		self.progress_label_error_img.hide()
		self.progress_label.set_text("")
		self.progress_bar.hide()
		self.update_btn.hide()

		self.main_window.connect("destroy",self.quit)
		self.set_css_info()
		self.connect_signals()
		self.init_threads()
		self.init_process()

	
	def set_css_info(self):
		
		self.style_provider=Gtk.CssProvider()

		f=Gio.File.new_for_path(self.css_file)
		self.style_provider.load_from_file(f)

		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.banner_box.set_name("BANNER_BOX")

	#def set-css_infoç
	def connect_signals(self):

		self.update_btn.connect("clicked",self.init_update)		

	#def connect_signals


	def init_process(self):

		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
		self.stack.set_visible_child_name("load")	
		self.stack.set_transition_duration(1000)
		self.loadBox.load_process()

	#def init_process

	def show_options(self,hide,error,msg=None):

		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
		self.stack.set_visible_child_name("options")

		if not hide:
			self.update_btn.show()
		self.optionsBox.show_info_panel(hide,error,msg)	

	#def show_options

	def init_threads(self):

		self.preactions_process_t=threading.Thread(target=self.preactions_process)
		self.update_process_t=threading.Thread(target=self.update_process)
		self.checkFinalFlavourToInstall_t=threading.Thread(target=self.checkFinalFlavourToInstall)
		self.postactions_process_t=threading.Thread(target=self.postactions_process)

		self.preactions_process_t.done=False
		self.update_process_t.done=False
		self.checkFinalFlavourToInstall_t.done=False
		self.postactions_process_t.done=False
		
		self.preactions_process_t.launched=False
		self.update_process_t.launched=False
		self.checkFinalFlavourToInstall_t.launched=False
		self.postactions_process_t.launched=False

	#def init_threads)


	def init_update(self,widget):

		self.update_btn.set_sensitive(False)
		self.number_process=4
		GLib.timeout_add(100,self.dist_upgrade)

	#def init_update

	def dist_upgrade(self):

		if not self.preactions_process_t.launched:
			print("  [Lliurex-Up]: Executing pre-actions")
			self.progress_label_box.show()
			self.progress_bar.show()
			self.core.optionsBox.terminal_btn.set_sensitive(True)
			self.preactions_process_t.start()
			self.preactions_process_t.launched=True
			self.show_number_process_executing(1,_("Preparing system to the update..."))

		else:

			if self.preactions_process_t.done:
				if not self.update_process_t.is_alive() and not self.update_process_t.launched:
					print("  [Lliurex-Up]: Executing dist-upgrade")
					self.update_process_t.start()
					self.update_process_t.launched=True
					self.show_number_process_executing(2,_("Downloading and installing packages..."))
					
				if self.update_process_t.done:
					if not self.postactions_process_t.is_alive() and not self.postactions_process_t.launched:
						print("  [Lliurex-Up]: Executing post-actions")
						self.postactions_process_t.start()
						self.postactions_process_t.launched=True
						self.show_number_process_executing(3,_("Ending the update..."))
					
					if self.postactions_process_t.done:

				
						if not self.checkFinalFlavourToInstall_t.is_alive() and not self.checkFinalFlavourToInstall_t.launched:
							print("  [Lliurex-Up]: Checking Final metapackage")
							self.checkFinalFlavourToInstall_t.start()
							self.checkFinalFlavourToInstall_t.launched=True
							self.show_number_process_executing(4,_("Checking metapackage..."))
										  			
						if self.checkFinalFlavourToInstall_t.done:				  
							self.core.packagesBox.update_state_icon()
							self.progress_label.set_halign(Gtk.Align.START)
							self.progress_bar_box.hide()

							if not self.core.llxUpConnect.checkErrorDistUpgrade():
								self.progress_label_box.set_name("SUCCESS_BOX")
								self.progress_label_ok_img.show()
								self.progress_label.set_text(_("The updated process has ended successfully.The system is now update"))

							else:
								self.progress_label_box.set_name("ERROR_BOX")
								self.progress_label_error_img.show()
								self.progress_label.set_text(_("The updated process has ended with errors"))
							
							return False	

		if self.preactions_process_t.launched:
			if 	not self.preactions_process_t.done:
				if not os.path.exists(self.core.llxUpConnect.preactions_token):
					return True
				else:
					self.preactions_process_t.done=True
					return True


		if self.update_process_t.launched:
			if 	not self.update_process_t.done:
				if not os.path.exists(self.core.llxUpConnect.upgrade_token):
					return True
				else:
					self.update_process_t.done=True	
					return True
					
		if self.postactions_process_t.launched:
			if 	not self.postactions_process_t.done:
				
				if not os.path.exists(self.core.llxUpConnect.postactions_token):
					return True
				else:
					self.postactions_process_t.done=True
					return True		

		

		if self.checkFinalFlavourToInstall_t.launched:
			if not self.checkFinalFlavourToInstall_t.done:
				if not os.path.exists(self.core.llxUpConnect.installflavour_token):
					return True
				else:
					self.checkFinalFlavourToInstall_t.done=True	
					return True				

			
	#def dist_upgrade


	def preactions_process(self):

		self.command=self.core.llxUpConnect.preActionsScript()
		length=len(self.command)
		self.core.terminalBox.vterminal.feed_child_binary(bytes(self.command,'utf8'))

	#def preactions_process
	
	def update_process(self):
		
		self.command=self.core.llxUpConnect.distUpgradeProcess()
		length=len(self.command)
		self.core.terminalBox.vterminal.feed_child_binary(bytes(self.command,'utf8'))

	#def update_process		


	def postactions_process(self):

		self.command=self.core.llxUpConnect.postActionsScript()
		length=len(self.command)
		self.core.terminalBox.vterminal.feed_child_binary(bytes(self.command,'utf8'))

	#def postactions_process

	
	def checkFinalFlavourToInstall(self):

		
		time.sleep(5)
		self.flavourToInstall=self.core.llxUpConnect.checkFinalFlavour()

		if len(self.flavourToInstall)>0:
			print("  [Lliurex-Up]: Check Final Metapackage: Instalation of metapackage is required")
			self.installFinalFlavour(self.flavourToInstall)
		else:
			print("  [Lliurex-Up]: Check Final Metapackage: Nothing to do")
			self.command='exit ' + '\n'
			length=len(self.command)
			self.core.terminalBox.vterminal.feed_child_binary(bytes(self.command,'utf8'))
			self.checkFinalFlavourToInstall_t.done=True	
	
	#def checkFinalFlavourToInstall

	def installFinalFlavour(self,flavourToInstall):

		self.command=self.core.llxUpConnect.installFinalFlavour(flavourToInstall)
		length=len(self.command)
		self.core.terminalBox.vterminal.feed_child_binary(bytes(self.command,'utf8'))

	#def installFinalFlavour

	def show_number_process_executing(self, execprocess, processname):

		self.total_process=self.number_process+1.0
		self.progress_bar.set_fraction(execprocess/self.total_process)
		if processname =="":
			msg_pbar=str(execprocess) + _(" of ") + str(self.number_process)
		else:
			msg_pbar=str(execprocess) + _(" of ") + str(self.number_process) + ". " + processname
	
		self.progress_label.set_text(msg_pbar)


	#def show_number_process_executing

				
	def quit(self,widget,event=None):

		self.llxup_connect.cleanEnvironment()
		self.llxup_connect.cleanLliurexUpLock()
		Gtk.main_quit()	

	#def quit	

	def start_gui(self):
		Gtk.main()

	#def start_gui

#class MainWindow
 
