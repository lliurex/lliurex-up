#!/usr/bin/env python
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('PangoCairo', '1.0')
gi.require_version('Vte', '2.91')

import cairo
import os
import shutil
import threading
import ConfigParser
import platform
import subprocess
import sys
import time
import commands
from gi.repository import Gtk, Gdk, GdkPixbuf, GObject, GLib, PangoCairo, Pango, Vte


import LliurexUpConnect

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

import gettext
gettext.textdomain('lliurex-up')
_ = gettext.gettext



BASE_DIR="/usr/share/lliurex-up/"
GLADE_FILE=BASE_DIR+"rsrc/lliurex-up.ui"
CACHED_ICON=BASE_DIR+"rsrc/cached.png"
DONE_ICON=BASE_DIR+"rsrc/done.png"
ERROR_ICON=BASE_DIR+"rsrc/error.png"
NEWPACKAGE_ICON=BASE_DIR +"rsrc/newpackage.png"
UPDATEPACKAGE_ICON=BASE_DIR + "rsrc/updatepackage.png" 	
DESKTOP_PATH="/usr/share/applications"
LOCK_PATH="/var/run/lliurexUp.lock"
DISABLE_INDICATOR_PATH="/etc/lliurex-up-indicator"
DISABLE_INDICATOR_TOKEN=os.path.join(DISABLE_INDICATOR_PATH,'disableIndicator.token')
TERMINAL_CONFIG=BASE_DIR+"terminal_config"



class Package:

	def __init__(self,installed,name,version,size):
		self.name=name
		self.version=version
		self.size=size
		desktop_file=os.path.join(DESKTOP_PATH,name+".desktop")
		self.parse_desktop(desktop_file)
		#self.parse_changelog(changelog_file)
		self.parse_installed_icon(CACHED_ICON)
		self.parse_newpackage_icon(installed)

	#def__init__
	
	def parse_desktop(self,desktop_file):
		
		try:
			config = ConfigParser.ConfigParser()
			config.optionxform=str

			config.read(desktop_file)
			
			#Zomandos may include a desktop file of type zomando with info for the store. Those desktops must be skipped
			if config.has_section("Desktop Entry") and config.has_option("Desktop Entry","Icon") and config.get("Desktop Entry","Type").lower()!="zomando":
				self.icon=config.get("Desktop Entry","Icon")
				icon_extension=os.path.splitext(self.icon)[1]
				if icon_extension==".xpm":
					self.icon="package"
			else:
				self.icon="package"
				
		except Exception as e:
			
			self.icon="package"
			
	#def parse_desktop

	def parse_installed_icon(self, icon_file):
		
			image=Gtk.Image()
			image.set_from_file(icon_file)		
			self.installed=image.get_pixbuf()


	#def parse_installed_icon


	def parse_newpackage_icon(self, installed):
		
			image=Gtk.Image()
			if installed==str(None):
				icon_file=NEWPACKAGE_ICON
			else:
				icon_file=UPDATEPACKAGE_ICON

			image.set_from_file(icon_file)		
			self.type=image.get_pixbuf()


class LliurexUp:

	def __init__(self):
		
		self.llxup_connect=LliurexUpConnect.LliurexUpConnect()
		self.check_root()
		self.isLliurexUpLocked()
					
	#def __init__		


	def isLliurexUpLocked(self):

		print "  [Lliurex-Up]: Checking if LliureX-Up is running..."

		code=self.llxup_connect.isLliurexUpLocked()

		if code !=0:
			message="Lliurex-Up"+self.getMessageDialog(code)
			self.showMessageDialog(code,message)
		else:
			self.isAptLocked()	
		
	#def islliurexup_running	


	def isAptLocked(self):

		print "  [Lliurex-Up]: Checking if Apt is running..."

		code=self.llxup_connect.isAptLocked()

		if code !=0:
			message="Apt"+self.getMessageDialog(code)
			self.showMessageDialog(code,message)
		
		else:
			self.isDpkgLocked()
	
	#def isAptLocked		


	def isDpkgLocked(self):

		print "  [Lliurex-Up]: Checking if Dpkg is running..."

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
			self.start_gui()
				

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
			dialog_buttons=Gtk.ButtonsType.CANCEL
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
			print "  [Lliurex-Up]: Checking root"
			f=open("/etc/lliurex-up.token","w")
			f.close()
			os.remove("/etc/lliurex-up.token")
		except:
			print "  [Lliurex-Up]: No administration privileges"
			dialog = Gtk.MessageDialog(None,0,Gtk.MessageType.ERROR, Gtk.ButtonsType.CANCEL, "Lliurex-Up")
			dialog.format_secondary_text(_("You need administration privileges to run this application."))
			dialog.run()
			sys.exit(1)
		
	#def check_root

	def start_gui(self):
		
		builder=Gtk.Builder()
		builder.set_translation_domain('lliurex-up')

		glade_path=GLADE_FILE
		builder.add_from_file(glade_path)

		self.stack = Gtk.Stack()
		self.stack.set_transition_duration(1000)
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)


		self.window=builder.get_object("main_window")
		self.window.resize(640,769)
		self.main_box=builder.get_object("main_box")
		self.pbar=builder.get_object("progressbar")
		self.pbar_label=builder.get_object("progressbar_label")
		

		self.cancel_button_box=builder.get_object("cancel_button_box")
		self.cancel_button_eb=builder.get_object("cancel_button_eventbox")
		self.cancel_button_eb.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK )
		self.cancel_button_eb.connect("button-press-event", self.quit)
		self.cancel_button_eb.connect("motion-notify-event", self.mouse_over_cancel)
		self.cancel_button_eb.connect("leave-notify-event", self.mouse_exit_cancel)
		self.cancel_button_label=builder.get_object("cancel_button_label")

		self.indicator_box=builder.get_object("indicator_box")
		self.indicator_label=builder.get_object("indicator_label")
		self.indicator_switch=builder.get_object("indicator_switch")

		
		if os.path.exists(DISABLE_INDICATOR_TOKEN):
			self.indicator_switch.set_active(False)
		else:
			self.indicator_switch.set_active(True)
	
		

		self.gather_box=builder.get_object("gather_box")
		self.yes_button_box=builder.get_object("yes_button_box")
		self.yes_button_eb=builder.get_object("yes_button_eventbox")
		self.yes_button_eb.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK )
		self.yes_button_eb.connect("button-release-event", self.yes_button_clicked)
		self.yes_button_eb.connect("motion-notify-event", self.mouse_over_yes)
		self.yes_button_eb.connect("leave-notify-event", self.mouse_exit_yes)
		self.yes_button_label=builder.get_object("yes_button_label")

		self.no_button_box=builder.get_object("no_button_box")
		self.no_button_eb=builder.get_object("no_button_eventbox")
		self.no_button_eb.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK )
		self.no_button_eb.connect("button-release-event", self.no_button_clicked)
		self.no_button_eb.connect("motion-notify-event", self.mouse_over_no)
		self.no_button_eb.connect("leave-notify-event",self.mouse_exit_no)
		self.no_button_label=builder.get_object("no_button_label")
		self.gather_logo_box=builder.get_object("gather_logo_box")
		self.gather_label=builder.get_object("gather_label")
		self.spinner=builder.get_object("spinner")

		self.update_box=builder.get_object("update_box")
		self.current_version_label=builder.get_object("current_version_label")
		self.current_version_label_info=builder.get_object("current_version_info_label")
		self.version_available_label=builder.get_object("version_available_label")
		self.version_available_label_info=builder.get_object("version_available_info_label")
		self.version_update_label=builder.get_object("version_update_label")
		self.version_update_label_info=builder.get_object("version_update_info_label")
		self.number_packages_label=builder.get_object("number_packages_label")
		self.number_packages_label_info=builder.get_object("number_packages_info_label")

		self.size_update_label=builder.get_object("size_update_label")
		self.size_update_label_info=builder.get_object("size_update_info_label")

		self.view_packages_button_box=builder.get_object("view_packages_button_box")
		self.view_packages_eb=builder.get_object("view_packages_eventbox")
		self.view_packages_eb.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK )
		self.view_packages_eb.connect("button-release-event", self.view_packages_clicked)
		self.view_packages_eb.connect("motion-notify-event", self.mouse_over_view_packages)
		self.view_packages_eb.connect("leave-notify-event", self.mouse_exit_view_packages)

		self.view_packages_label=builder.get_object("view_packages_label")

		self.update_button_box=builder.get_object("update_button_box")
		self.update_button_eb=builder.get_object("update_button_eventbox")
		self.update_button_eb.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)
		self.update_button_eb.connect("button-release-event", self.upgrade_process)
		self.update_button_eb.connect("motion-notify-event", self.mouse_over_update_button)
		self.update_button_eb.connect("leave-notify-event", self.mouse_exit_update_button)

		self.update_button_label=builder.get_object("update_button_label")
		self.update_button_label.set_label(_("Update now"))
		self.update_button_label.set_width_chars(20)
		self.update_button_label.set_max_width_chars(20)

		self.terminal_label=builder.get_object("terminal_label")
		self.viewport=builder.get_object("viewport")
		self.terminal_scrolled=builder.get_object("terminalScrolledWindow")
		self.vterminal=Vte.Terminal()
		self.vterminal.spawn_sync(
			Vte.PtyFlags.DEFAULT,
			os.environ['HOME'],
			#["/usr/sbin/dpkg-reconfigure", "xdm"],
			["/bin/bash","--rcfile",TERMINAL_CONFIG],
			[],
			GLib.SpawnFlags.DO_NOT_REAP_CHILD,
			None,
			None,
		)
		font_terminal = Pango.FontDescription("monospace normal 10")
		self.vterminal.set_font(font_terminal)
		self.vterminal.set_scrollback_lines(-1)
		self.vterminal.set_sensitive(False)
		self.terminal_scrolled.add(self.vterminal)
		

		self.packages_box=builder.get_object("packages_box")
		self.return_arrow_box=builder.get_object("return_arrow_box")
		self.return_arrow_eb=builder.get_object("return_arrow_eventbox")
		self.return_arrow_eb.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)
		self.return_arrow_eb.connect("button-release-event", self.arrow_clicked)
		self.return_arrow_eb.connect("motion-notify-event",self.mouse_over_return_arrow)
		self.return_arrow_eb.connect("leave-notify-event",self.mouse_exit_return_arrow)
		self.packages_label=builder.get_object("packages_label")
		self.packages_tv=builder.get_object("packages_treeview")
		self.changelog_texview=builder.get_object("changelog_textview")

		#self.packages_store=Gtk.ListStore(str,str,str,GdkPixbuf.Pixbuf)
		self.packages_store=Gtk.ListStore(GdkPixbuf.Pixbuf,str,str,str,GdkPixbuf.Pixbuf)
		self.packages_tv.set_model(self.packages_store)

		column=Gtk.TreeViewColumn("")
		cell=Gtk.CellRendererPixbuf()
		column.pack_start(cell,True)
		column.add_attribute(cell,"pixbuf",0)
		self.packages_tv.append_column(column)

		column=Gtk.TreeViewColumn("")
		cell=Gtk.CellRendererPixbuf()
		cell.set_property("stock-size",Gtk.IconSize.DIALOG)
		column.pack_start(cell,True)
		column.add_attribute(cell,"icon-name",1)
		self.packages_tv.append_column(column)
		
		column=Gtk.TreeViewColumn(_("Package"))
		cell=Gtk.CellRendererText()
		column.pack_start(cell,True)
		column.add_attribute(cell,"markup",2)
		column.set_expand(True)

		
		self.packages_tv.append_column(column)
		self.packages_tv.connect("button-release-event",self.package_clicked)
		
		column=Gtk.TreeViewColumn(_("Size"))
		cell=Gtk.CellRendererText()
		cell.set_property("alignment",Pango.Alignment.CENTER)
		column.pack_start(cell,False)
		column.add_attribute(cell,"markup",3)
		self.packages_tv.append_column(column)		

		column=Gtk.TreeViewColumn(_("State"))
		cell=Gtk.CellRendererPixbuf()
		column.pack_start(cell,True)
		column.add_attribute(cell,"pixbuf",4)
		self.packages_tv.append_column(column)
		
		self.changelog_textview=builder.get_object("changelog_textview")
		self.changelog_label=builder.get_object("changelog_label")


		self.stack.add_titled(self.gather_box,"gather","Gather")
		self.stack.add_titled(self.update_box,"update", "Update")
		self.stack.add_titled(self.packages_box, "packages", "Packages")

		self.main_box.pack_start(self.stack,True,False,5)

		self.window.show_all()
		self.terminal_scrolled.hide()
		self.viewport.hide()
		self.terminal_label.hide()
		self.cancel_button_box.hide()
		self.indicator_box.hide()
		self.yes_button_box.hide()
		self.no_button_box.hide()

		self.pbar_label.show()
		self.pbar.show()
		
		self.window.connect("destroy",self.quit)
		
		self.set_css_info()

		msg_gather="<span><b>"+_("Checking system")+"</b></span>"
		self.gather_label.set_markup(msg_gather)
		GLib.timeout_add(100,self.pulsate_checksystem)

		self.initactions_process_t=threading.Thread(target=self.initActions_process)
		self.check_lliurexup_t=threading.Thread(target=self.check_lliurexup_version)
		self.install_lliurexup_t=threading.Thread(target=self.install_lliurexup)
		self.check_mirror_t=threading.Thread(target=self.check_mirror)
		#self.wait_response_t=threading.Thread(target=self.wait_response)
		self.execute_lliurexmirror_t=threading.Thread(target=self.execute_lliurexmirror)
		self.get_lliurexversionlocal_t=threading.Thread(target=self.get_lliurexversionlocal)
		self.get_lliurexversionnet_t=threading.Thread(target=self.get_lliurexversionnet)
		self.checkInitialFlavourToInstall_t=threading.Thread(target=self.checkInitialFlavourToInstall)
		self.gather_packages_t=threading.Thread(target=self.gather_packages)
		self.preactions_process_t=threading.Thread(target=self.preactions_process)
		self.update_process_t=threading.Thread(target=self.update_process)
		self.checkFinalFlavourToInstall_t=threading.Thread(target=self.checkFinalFlavourToInstall)
		self.postactions_process_t=threading.Thread(target=self.postactions_process)

		self.initactions_process_t.daemon=True
		self.check_lliurexup_t.daemon=True
		self.install_lliurexup_t.daemon=True
		self.check_mirror_t.daemon=True
		self.execute_lliurexmirror_t.daemon=True
		self.get_lliurexversionlocal_t.daemon=True
		self.get_lliurexversionnet_t.daemon=True
		self.checkInitialFlavourToInstall_t.daemon=True
		self.gather_packages_t.daemon=True
		self.preactions_process_t.daemon=True
		self.update_process_t.daemon=True
		self.checkFinalFlavourToInstall_t.daemon=True
		self.postactions_process_t.daemon=True

		self.initactions_process_t.done=False
		self.check_lliurexup_t.done=False
		self.install_lliurexup_t.done=False
		self.check_mirror_t.done=False
		self.execute_lliurexmirror_t.done=False
		self.get_lliurexversionlocal_t.done=False
		self.get_lliurexversionnet_t.done=False
		self.checkInitialFlavourToInstall_t.done=False
		self.gather_packages_t.done=False
		self.preactions_process_t.done=False
		self.update_process_t.done=False
		self.checkFinalFlavourToInstall_t.done=False
		self.postactions_process_t.done=False
		
		self.initactions_process_t.launched=False
		self.check_lliurexup_t.launched=False
		self.install_lliurexup_t.launched=False
		self.check_mirror_t.launched=False
		self.execute_lliurexmirror_t.launched=False
		self.get_lliurexversionlocal_t.launched=False
		self.get_lliurexversionnet_t.launched=False
		self.checkInitialFlavourToInstall_t.launched=False
		self.gather_packages_t.launched=False
		self.preactions_process_t.launched=False
		self.update_process_t.launched=False
		self.checkFinalFlavourToInstall_t.launched=False
		self.postactions_process_t.launched=False
		
		self.spinner.start()
		self.package_list=[]
		self.max_seconds=5.0
		self.current_second=0
		self.number_process=8

		GObject.threads_init()
		Gtk.main()

	#def start_gui
	
	def set_css_info(self):
	
		css = """


		#WHITE_BACKGROUND {
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#ffffff),  to (#ffffff));;
		
		}

		#BUTTON_LABEL{
			color:white;
			font: 10pt Roboto;
		}

		#DISABLED_BUTTON_OVER{
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#888888),  to (#888888));;
		}
		
		#DISABLED_BUTTON{
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#666666),  to (#666666));;
		}
		
		#CANCEL_BUTTON{
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#D32F2F),  to (#D32F2F));;
		}
		
		#CANCEL_BUTTON_OVER{
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#F44336),  to (#F44336));;
		}

		#BUTTON_COLOR {
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#448AFF),  to (#448AFF));;
		
		}
		
		#BUTTON_OVER_COLOR {
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#449fff),  to (#449fff));;
			
		
		}

		#UPDATE_BUTTON_LABEL{
			color:white;
			font: 11pt Roboto;
		}
		
		#UPDATE_CORRECT_BUTTON_COLOR {
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#979797),  to (#979797));;
		
		}

		#UPDATE_OVER_COLOR {
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#53b757),  to (#53b757));;
		
		}


		#UPDATE_ERROR_BUTTON_COLOR {
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#D32F2F),  to (#D32F2F));;
		
		}

		#UPDATE_LAUNCHED_OVER_COLOR {
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#F44336),  to (#F44336));;
		
		}

		#UPDATE_BUTTON_LAUNCHED_COLOR {
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#7cadff), to (#7cadff));;

		}
				
		#GATHER_ICON_COLOR {
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#b0bec5),  to (#b0bec5));;
		
		}
		
		
		#BLUE_FONT {
			color: #3366cc;
			font: 11pt Roboto Bold;
			
		}	
		

		#CHANGELOG_FONT {
			color: #3366cc;
			font: 11pt Roboto;
			
		}

		#LABEL_OPTION{
		
			color: #808080;
			font: 11pt Roboto;
		}

		#ERROR_FONT {
			color: #CC0000;
			font: 11pt Roboto Bold; 
		}

		#CORRECT_FONT {
			color: #43a047;
			font: 11pt Roboto Bold;

		}
		
		#DISABLED_BUTTON{
			background-image:-gtk-gradient (linear,	left top, left bottom, from (#666666),  to (#666666));;
		}
		"""

		self.style_provider=Gtk.CssProvider()
		self.style_provider.load_from_data(css)
		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		
		self.window.set_name("WHITE_BACKGROUND")
		self.update_box.set_name("WHITE_BACKGROUND")
		self.gather_box.set_name("WHITE_BACKGROUND")
		self.packages_box.set_name("WHITE_BACKGROUND")
		self.gather_label.set_name("CHANGELOG_FONT")
		self.pbar_label.set_name("CHANGELOG_FONT")

		self.yes_button_box.set_name("BUTTON_COLOR")
		self.yes_button_label.set_name("BUTTON_LABEL")

		self.no_button_box.set_name("BUTTON_COLOR")
		self.no_button_label.set_name("BUTTON_LABEL")

		self.view_packages_button_box.set_name("BUTTON_COLOR")
		self.view_packages_label.set_name("BUTTON_LABEL")

		self.cancel_button_box.set_name("BUTTON_COLOR")
		self.cancel_button_label.set_name("BUTTON_LABEL")
		self.indicator_label.set_name("LABEL_OPTION")	

		self.current_version_label.set_name("LABEL_OPTION")
		self.version_available_label.set_name("LABEL_OPTION")
		self.version_update_label.set_name("LABEL_OPTION")	
		self.number_packages_label.set_name("LABEL_OPTION")
		self.size_update_label.set_name("LABEL_OPTION")
		self.update_button_label.set_name("UPDATE_BUTTON_LABEL")
		self.update_button_box.set_name("BUTTON_COLOR")
		self.terminal_label.set_name("CHANGELOG_FONT")
		self.current_version_label_info.set_name("BLUE_FONT")
		self.version_available_label_info.set_name("BLUE_FONT")
		self.version_update_label_info.set_name("BLUE_FONT")
		self.number_packages_label_info.set_name("BLUE_FONT")
		self.size_update_label_info.set_name("BLUE_FONT")


		self.packages_label.set_name("LABEL_OPTION")
		#self.changelog_label.set_name("LABEL_OPTION")
		self.changelog_texview.set_name("CHANGELOG_FONT")
		self.return_arrow_box.set_name("BUTTON_COLOR")
		
	#def set_css_info	


	def pulsate_checksystem(self):

		abort=False
		if not self.initactions_process_t.launched:
			print "  [Lliurex-Up]: Checking system: connection to lliurex.net and init-actions"
			self.initactions_process_t.start()
			self.initactions_process_t.launched=True
			self.show_number_process_executing(1,"")
		
		if self.initactions_process_t.done:
			if self.free_space:
				if self.statusN4d:
					if self.can_connect:
						if self.is_mirror_running_inserver==False:

							if  not self.check_lliurexup_t.is_alive() and not self.check_lliurexup_t.launched:
								print "  [Lliurex-Up]: Checking Lliurex-Up version"
							 	msg_gather="<span><b>"+_("Looking for new version of LliureX Up")+"</b></span>"
								self.gather_label.set_markup(msg_gather)
							 	self.check_lliurexup_t.start()
						 		self.check_lliurexup_t.launched=True
						 		self.show_number_process_executing(2,"")


						 	if  self.check_lliurexup_t.done:
								if not self.is_lliurexup_updated:
									if  not self.install_lliurexup_t.is_alive() and not self.install_lliurexup_t.launched:
										print "  [Lliurex-Up]: Updating Lliurex-Up"
										msg_gather="<span><b>"+_("Updating LliureX Up")+"</b></span>"
										self.gather_label.set_markup(msg_gather)
										self.install_lliurexup_t.start()
										self.install_lliurexup_t.launched=True
										self.show_number_process_executing(3,"")

									else:
										if self.install_lliurexup_t.done:
											print "  [Lliurex-Up]: Reboot Lliurex-Up"
											self.pbar_label.hide()
											self.msg_wait="<span><b>"+_("LliureX Up is now updated and will be reboot in %s seconds...")+"</b></span>"
											GLib.timeout_add(10,self.wait_to_reboot)
											return False
								else:
									if not self.check_mirror_t.is_alive() and not self.check_mirror_t.launched:
										print "  [Lliurex-Up]: Checking if mirror exist"
										msg_gather="<span><b>"+_("Checking if mirror exist and there is updated")+"</b></span>"
										self.gather_label.set_markup(msg_gather)
										self.check_mirror_t.start()
										self.check_mirror_t.launched=True
										self.show_number_process_executing(4,"")
								
									if 	self.check_mirror_t.done:
										is_mirror_running=self.llxup_connect.lliurexMirrorIsRunning()

										if not self.is_mirror_updated:
											if not is_mirror_running:
												print "  [Lliurex-Up]: Asking if mirror will be update"
												self.yes_button_box.show()
												self.no_button_box.show()
												self.pbar.hide()
												self.pbar_label.hide()
												msg_gather="<span><b>"+_("Your mirror is not update. Do you want to update it?")+"</b></span>"
												self.gather_label.set_markup(msg_gather)
												return False

											else:
												self.mirror_running_msg()
												return False

										else:	
											if is_mirror_running:
												self.mirror_running_msg()
												return False
											else:	
												print "  [Lliurex-Up]: Nothing to do with mirror"
												GLib.timeout_add(100,self.pulsate_get_info)
												return False
					
						else:
							abort=True
							if self.is_mirror_running_inserver:
								msg_gather="<span><b>"+_("Mirror is being updated in server. Unable to update the system")+"</b></span>"
								print "  [Lliurex-Up]: Mirror is being updated in server"
							else:
								msg_gather="<span><b>"+_("Unable to connect with server")+"</b></span>"
								print "  [Lliurex-Up]: Unable to connect with server"

					else:
						abort=True
						msg_gather="<span><b>"+_("Unable to connect to lliurex.net")+"</b></span>"
						print "  [Lliurex-Up]: Unable to connect to lliurex.net"

				else:
					abort=True
					msg_gather="<span><b>"+_('N4d is not working. Restart the service and try againg')+"</b></span>"
					print "  [Lliurex-Up]: N4d is not working"
			else:
				abort=True
				msg_gather="<span><b>"+_("There's not enough space on disk to upgrade (2 GB needed)")+"</b></span>"
				print "  [Lliurex-Up]: Not enough space on disk"
								
		if abort:
			self.spinner.stop()
			self.pbar.hide()
			self.pbar_label.hide()
			self.cancel_button_box.show()
			self.show_indicator_switch()
			self.gather_label.set_name("ERROR_FONT")
			self.gather_label.set_markup(msg_gather)
			return False
		
				
		if self.initactions_process_t.is_alive():
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

		
	#def pulsate_checksystem	

	def wait_to_reboot(self):

		csecond=int(self.max_seconds+1-self.current_second)
		self.gather_label.set_markup(self.msg_wait%csecond)
		self.pbar.set_fraction(self.current_second/self.max_seconds)

		self.current_second+=0.01

		if self.current_second>=self.max_seconds:
			self.llxup_connect.cleanLliurexUpLock()
			os.execl(sys.executable, sys.executable, *sys.argv)	
			return False
		else:
			return True

	#def wait_to_reboot

	
	def initActions_process(self):
		time.sleep(5)
		self.free_space=self.llxup_connect.free_space_check()
		if self.free_space:
			self.statusN4d=self.llxup_connect.checkInitialN4dStatus()
			if self.statusN4d:
				self.llxup_connect.checkInitialFlavour()
				self.can_connect=self.llxup_connect.canConnectToLliurexNet()
				if self.can_connect:
					self.is_mirror_running_inserver=self.llxup_connect.clientCheckingMirrorIsRunning()
					self.llxup_connect.initActionsScript()

		self.initactions_process_t.done=True
	
	def check_lliurexup_version(self):

		#time.sleep(5)	
		self.is_lliurexup_updated=self.llxup_connect.isLliurexUpIsUpdated()
		self.check_lliurexup_t.done=True
		
	#def check_lliurexup_version	
		
	def install_lliurexup(self):

		self.is_lliurexup_installed=self.llxup_connect.installLliurexUp()
		self.install_lliurexup_t.done=True

	#def install_lliurexup 	

		
	def check_mirror(self):

		self.is_mirror_updated=self.llxup_connect.lliurexMirrorIsUpdated()
		self.check_mirror_t.done=True
	
	#def check_mirror	

	def no_button_clicked(self,widget,event):
		
		#self.response=0
		self.pbar.show()
		self.pbar_label.show()	
		GLib.timeout_add(100,self.pulsate_get_info)
		self.yes_button_box.hide()
		self.no_button_box.hide()
		log_msg="Update lliurex-mirror: No"
		self.llxup_connect.log(log_msg)

	#def def no_button_clicked
		
	def yes_button_clicked(self,widget,event):
	
		self.pbar.show()
		self.pbar_label.show()
		print "[Lliurex-Up]: Updating mirror"
		self.updated_percentage(0)
		self.yes_button_box.hide()
		self.no_button_box.hide()
		self.execute_lliurexmirror_t.start()
		self.mirror_running_msg()
		log_msg="Update lliurex-mirror: Yes"
		print log_msg
		self.llxup_connect.log(log_msg)

	#def yes_button_clicked

	def pulsate_updating_mirror(self):

		self.is_mirror_running=self.llxup_connect.lliurexMirrorIsRunning()

		if self.is_mirror_running or self.execute_lliurexmirror_t.is_alive():
			mirror_percentage=self.llxup_connect.getPercentageLliurexMirror()
			self.updated_percentage(mirror_percentage)
			return True
		
		else:
			GLib.timeout_add(100,self.pulsate_get_info)
			return False	

	#def pulsate_updating_mirro		

	def execute_lliurexmirror(self):
		
		commands.getoutput('/usr/sbin/lliurex-mirror-gui')

	#def def execute_lliurexmirror	

	def mirror_running_msg(self):

		self.spinner.start()
		msg_gather="<span><b>"+_("Mirror is being updated. The process may take several minutes")+"</b></span>"
		self.gather_label.set_markup(msg_gather)
		GLib.timeout_add(1000,self.pulsate_updating_mirror)

	#def mirror_running_msg	


	def pulsate_get_info(self):

		#self.pbar.pulse()
 
		if not self.get_lliurexversionlocal_t.launched:
			print "  [Lliurex-Up]: Looking for LliurexVersion from local repository "
			msg_gather="<span><b>"+_("Looking for new version to update")+"</b></span>"
			self.gather_label.set_markup(msg_gather)
			self.get_lliurexversionlocal_t.start()
			self.get_lliurexversionlocal_t.launched=True
			self.show_number_process_executing(5,"")



		if self.get_lliurexversionlocal_t.done:
			if not self.get_lliurexversionnet_t.is_alive() and not self.get_lliurexversionnet_t.launched:
				print "  [Lliurex-Up]: Looking for LliurexVersion from Lliurex net"
				msg_gather="<span><b>"+_("Looking for new version available")+"</b></span>"
				self.gather_label.set_markup(msg_gather)
				self.get_lliurexversionnet_t.start()	
				self.get_lliurexversionnet_t.launched=True
				self.show_number_process_executing(6,"")



			if self.get_lliurexversionnet_t.done:

				if not self.checkInitialFlavourToInstall_t.is_alive() and not self.checkInitialFlavourToInstall_t.launched:
					print "  [Lliurex-Up]: Checking if installation of metapackage is required"
					msg_gather="<span><b>"+_("Checking if installation of metapackage is required")+"</b></span>"
					self.gather_label.set_markup(msg_gather)
					self.checkInitialFlavourToInstall_t.start()
					self.checkInitialFlavourToInstall_t.launched=True
					self.show_number_process_executing(7,"")



				if self.checkInitialFlavourToInstall_t.done:

	 				if not self.gather_packages_t.is_alive() and not self.gather_packages_t.launched:
						print "  [Lliurex-Up]: Looking for for new updates"
						msg_gather="<span><b>"+_("Looking for new updates")+"</b></span>"
						self.gather_label.set_markup(msg_gather)
						self.gather_packages_t.start()
						self.gather_packages_t.launched=True
						self.show_number_process_executing(8,"")


					if self.gather_packages_t.done:
						self.spinner.stop()
						self.pbar.hide()
						self.pbar_label.hide()
						self.cancel_button_box.show()	
						self.show_indicator_switch()

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
										self.gather_label.set_name("ERROR_FONT")
										msg_gather="<span><b>"+_("Updated abort. An error occurred in the search for updates")+"</b></span>"
										self.gather_label.set_markup(msg_gather)
										log_msg="Updated abort. An error occurred in the search for updates"
										self.llxup_connect.log(log_msg)
										print "  [Lliurex-Up]: Error in search for updates"
										return False
								else:
									self.show_indicator_switch()
									self.cancel_button_label.set_label(_("Close"))
									msg_gather="<span><b>"+_("Your system is update")+"</b></span>"
									self.gather_label.set_markup(msg_gather)
									log_msg="System update. Nothing to do"
									self.llxup_connect.log(log_msg)
									print "  [Lliurex-Up]: System update. Nothing to do"
									return False
													
						else:
							if not self.incorrect_flavours:

								print "  [Lliurex-Up]: System nor update"	

								#self.requires_installing_metapackage()
								self.parse_packages_updated()
								self.populate_packages_tv()
								self.get_update_summary()
								self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
								self.stack.set_visible_child_name("update")	
								return False
							else:
								self.gather_label.set_name("ERROR_FONT")
								msg_gather="<span><b>"+_("Updated abort for incorrect metapackages detected in update")+"</b></span>"
								self.gather_label.set_markup(msg_gather)
								log_msg="Updated abort for incorrect metapackages detected in update"
								self.llxup_connect.log(log_msg)
								print "  [Lliurex-Up]: Update abort. Detect incorrect metapackages in new updates"
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
		self.version_update=self.llxup_connect.getLliurexVersionLocal()
		self.get_lliurexversionlocal_t.done=True

	#def get_lliurexversionlocal
	
	def get_lliurexversionnet(self):
		self.version_available=self.llxup_connect.getLliurexVersionNet()
		self.get_lliurexversionnet_t.done=True


	#def get_lliurexversionlocal	
	
	def checkInitialFlavourToInstall(self):
		self.is_flavour_installed=0
		self.targetMetapackage=self.llxup_connect.targetMetapackage

		if self.targetMetapackage == None:
			print "  [Lliurex-Up]: Installation of metapackage is not required"
			self.checkInitialFlavourToInstall_t.done=True	

		else:
			print "  [Lliurex-Up]: Installation of metapackage is required: " +str(self.targetMetapackage)
			self.is_flavour_installed=self.llxup_connect.installInitialFlavour(self.targetMetapackage)	
			self.checkInitialFlavourToInstall_t.done=True			

	#def checkInitialFlavourToInstall(
	
	def gather_packages(self):

		self.packages,self.size_update=self.llxup_connect.getPackagesToUpdate()
		self.incorrect_flavours=self.llxup_connect.checkIncorrectFlavours()
		self.gather_packages_t.done=True

		
	#def gather_info


	def get_update_summary(self):

		if self.version_update["installed"]==None:
			msg_current_version_info=_("Not available")

		else:
			msg_current_version_info=str(self.version_update["installed"])


		if self.version_available==None:
			if 'client' in self.llxup_connect.previousFlavours or self.targetMetapackage=='lliurex-meta-client':
		  		msg_version_available_info=_("Not available for clients")

			else:
				self.version_available_label_info.set_name("ERROR_FONT")
				msg_version_available_info=_("Not available. Check conexion to lliurex.net")

		else:
			msg_version_available_info=self.version_available


		if self.version_update["candidate"]==None:
			msg_version_update_info=_("Not available")

		else:
			msg_version_update_info=self.version_update["candidate"]

		self.number_pkg=len(self.packages)
		 
		self.size_update_label.show()

		msg_number_info=str(self.number_pkg)+ " ("  +str(self.newpackages)+ _(" new)")

		msg_size=self.size_update

		
		self.current_version_label_info.set_markup(msg_current_version_info)
		self.version_available_label_info.set_markup(msg_version_available_info)
		self.version_update_label_info.set_markup(msg_version_update_info)
		self.number_packages_label_info.set_markup(msg_number_info)
		self.size_update_label_info.set_markup(msg_size)
		
	#def get_update_summary	
		
	def updated_percentage(self,completed):

		percentage=completed/100.0

		self.pbar.set_fraction(percentage)
		
		msg_value=format(completed,'.0f')
		
		msg_percentage="<span><b>"+msg_value+"%"+"</b></span>"
		self.pbar_label.set_markup(msg_percentage)
		
		
	#def updated_percentage
		
	def show_number_process_executing(self, execprocess, processname):

		self.total_process=self.number_process+1.0
		self.pbar.set_fraction(execprocess/self.total_process)
		if processname =="":
			msg_pbar=_("Executing process: ") + str(execprocess) + _(" of ") + str(self.number_process)
		else:
			msg_pbar=_("Executing process: ") + str(execprocess) + _(" of ") + str(self.number_process) + ". " + processname
	
		msg_pbar="<span><b>"+msg_pbar+"</b></span>" 
		self.pbar_label.set_markup(msg_pbar)

	#def show_number_process_executing
	
	def populate_packages_tv(self):
		
		for package in self.package_list:
			self.packages_store.append((package.type,package.icon,"<span font='Roboto'><b>"+package.name+"</b></span>\n"+"<span font='Roboto' size='small'>"+package.version+"</span>","<span font='Roboto' size='small'>"+package.size+"</span>", package.installed))
			
	#def populate_packages_tv
	
	def parse_packages_updated(self):
		
		self.newpackages=0	
		for item in self.packages:
			tmp=item.split(";")
			if len(tmp)>1:
				pack=Package(tmp[3],tmp[0],tmp[1],tmp[2])
				self.package_list.append(pack)
				if tmp[3]==str(None):
					self.newpackages=int(self.newpackages)+1	

	#def parse_simulate_output
	
	def package_clicked(self,x,y):

		default_text="Downloading changelog..."
		selection=self.packages_tv.get_selection()
		model,iter=selection.get_selected()
		self.changelog_textview.get_buffer().set_text("".join(default_text))

		name=model[iter][2]
		name=name[name.find("<b>")+3:name.find("</b>")]
		changelog=self.llxup_connect.getPackageChangelog(name)
		self.changelog_textview.get_buffer().set_text("".join(changelog))
		
	
	#def package_clicked			

	def upgrade_process(self,widget, event=None):

		
		self.msg_upgrade_running=_("The update process is running. Wait a moment please")

		if not self.preactions_process_t.launched:
			self.number_process=4
			self.pbar.show()
			self.viewport.show()
			self.terminal_scrolled.show()
			self.terminal_label.show()
			self.msg_terminal=_("Update process details")
			self.terminal_label.set_markup(self.msg_terminal)
			GLib.timeout_add(100,self.dist_upgrade)

		else:
			if not self.postactions_process_t.done:
				self.terminal_label.set_name("ERROR_FONT")
				self.terminal_label.set_markup(self.msg_upgrade_running)

	#def upgrade_process
	
	def dist_upgrade(self):

		if not self.preactions_process_t.launched:
			print "  [Lliurex-Up]: Executing pre-actions"
	  		self.pbar_label.show()
	  		self.cancel_button_box.hide()
	  		self.indicator_box.hide()

			self.preactions_process_t.start()
			self.preactions_process_t.launched=True
			self.show_number_process_executing(1,_("Preparing system to the update"))
			self.update_button_label.set_text(_("Updating"))
			self.update_button_box.set_name("UPDATE_BUTTON_LAUNCHED_COLOR")

		else:

			if self.preactions_process_t.done:
				if not self.update_process_t.is_alive() and not self.update_process_t.launched:
				 	print "  [Lliurex-Up]: Executing dist-upgrade"
				 	self.update_process_t.start()
				  	self.update_process_t.launched=True
				  	self.show_number_process_executing(2,_("Downloading and installing packages"))

			 	
				if self.update_process_t.done:
					if not self.postactions_process_t.is_alive() and not self.postactions_process_t.launched:
						print "  [Lliurex-Up]: Executing post-actions"
						self.postactions_process_t.start()
						self.postactions_process_t.launched=True
						self.show_number_process_executing(3,_("Ending the update"))
					
					if self.postactions_process_t.done:

				
						if not self.checkFinalFlavourToInstall_t.is_alive() and not self.checkFinalFlavourToInstall_t.launched:
							print "  [Lliurex-Up]: Checking Final metapackage"
							self.checkFinalFlavourToInstall_t.start()
							self.checkFinalFlavourToInstall_t.launched=True
							self.show_number_process_executing(4,_("Checking metapackage"))
										  			
				  				
				  		if self.checkFinalFlavourToInstall_t.done:				  
							self.cancel_button_box.show()
							self.show_indicator_switch()
							self.cancel_button_label.set_label(_("Close"))
							self.pbar.hide()
							self.pbar_label.hide()
							self.update_installed_icon()
								
							self.terminal_label.set_name("CHANGELOG_FONT")
							  			
							if not self.llxup_connect.checkErrorDistUpgrade():
								self.terminal_label.set_name("CORRECT_FONT")
								self.msg_upgrade_running="<span><b>" + _("The system is now update") + "</b></span>"
								self.update_button_label.set_text(_("Update successfully"))
								self.update_button_box.set_name("UPDATE_CORRECT_BUTTON_COLOR")

							else:
								self.terminal_label.set_name("ERROR_FONT")
								self.msg_upgrade_running="<span><b>" + _("The updated process has ended with errors") + "</b></span>"
								self.update_button_label.set_text(_("Update error"))
								self.update_button_box.set_name("UPDATE_ERROR_BUTTON_COLOR")
	
							
							self.terminal_label.set_markup(self.msg_upgrade_running)
					 		return False	
 	

		if self.preactions_process_t.launched:
			if 	not self.preactions_process_t.done:
				if not os.path.exists(self.llxup_connect.preactions_token):
					return True
				else:
					self.preactions_process_t.done=True
					return True


		if self.update_process_t.launched:
			if 	not self.update_process_t.done:
				if not os.path.exists(self.llxup_connect.upgrade_token):
					return True
				else:
					self.update_process_t.done=True	
					return True
					
		if self.postactions_process_t.launched:
			if 	not self.postactions_process_t.done:
				
				if not os.path.exists(self.llxup_connect.postactions_token):
					return True
				else:
					self.postactions_process_t.done=True
					return True		

		

		if self.checkFinalFlavourToInstall_t.launched:
			if not self.checkFinalFlavourToInstall_t.done:
				if not os.path.exists(self.llxup_connect.installflavour_token):
					return True
				else:
					self.checkFinalFlavourToInstall_t.done=True	
					return True				

			
	#def dist_upgrade


	def preactions_process(self):

		self.command=self.llxup_connect.preActionsScript()
		length=len(self.command)
		self.vterminal.feed_child(self.command, length)

	#def preactions_process
	
	def update_process(self):
		 
	 	self.command=self.llxup_connect.distUpgradeProcess()
	 	length=len(self.command)
	 	self.vterminal.feed_child(self.command, length)

	#def update_process		


	def postactions_process(self):

		self.command=self.llxup_connect.postActionsScript()
		length=len(self.command)
		self.vterminal.feed_child(self.command, length)

	#def postactions_process

	
	def checkFinalFlavourToInstall(self):

		
		time.sleep(5)
		self.flavourToInstall=self.llxup_connect.checkFinalFlavour()

		if self.flavourToInstall !=None:
			print "  [Lliurex-Up]: Check Final Metapackage: Instalation of metapackage is required"
			self.installFinalFlavour(self.flavourToInstall)
		else:
			print "  [Lliurex-Up]: Check Final Metapackage: Nothing to do"
			self.command='exit ' + '\n'
			length=len(self.command)
			self.vterminal.feed_child(self.command, length)
			self.checkFinalFlavourToInstall_t.done=True	
	
	#def checkFinalFlavourToInstall

	def installFinalFlavour(self,flavourToInstall):

		self.command=self.llxup_connect.installFinalFlavour(flavourToInstall)
	 	length=len(self.command)
	 	self.vterminal.feed_child(self.command, length)
	 			
	#def installFinalFlavour
	
	
	def view_packages_clicked(self,widget,event):

		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
		self.stack.set_visible_child_name("packages")
		
	#def view_packages_clicked	
	

	def arrow_clicked(self,widget,event):
	
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_RIGHT)
		self.stack.set_visible_child_name("update")	
		
	#def arrow_clicked

	def update_installed_icon(self):
	
		imagok=Gtk.Image()
		imagok.set_from_file(DONE_ICON)		
		iconok=imagok.get_pixbuf()

		imagerr=Gtk.Image()
		imagerr.set_from_file(ERROR_ICON)		
		iconerr=imagerr.get_pixbuf()
		packages_status=self.llxup_connect.getStatusPackage()

		for item in self.packages_store:
		 	name=item[2].split(">")[2]
		 	name=name.split("<")[0]
		 	version=item[2].split(">")[5]
		 	version=version.split("<")[0]
		 	tmp=str(name)+"_"+str(version)
		 	if tmp in packages_status:
		 		item[4]=iconok
			else:
				item[4]=iconerr
			
	#def update_installed_icon	

	def mouse_over_yes(self,widget,event):

		self.yes_button_box.set_name("BUTTON_OVER_COLOR")

	#def mouse_over_yes 	

	def mouse_exit_yes(self,widget,event):

		self.yes_button_box.set_name("BUTTON_COLOR")

	#def mouse_exit_yes	

	def mouse_over_no(self,widget,event):

		self.no_button_box.set_name("BUTTON_OVER_COLOR")

	#def mouse_over_no	

	def mouse_exit_no(self,widget,event):

		self.no_button_box.set_name("BUTTON_COLOR")

	#def mouse_exit_no	
			
	def mouse_over_view_packages(self,widget,event):

		self.view_packages_button_box.set_name("BUTTON_OVER_COLOR")	

	#def mouse_over_view_packages	

	def mouse_exit_view_packages(self,widget,event):

		self.view_packages_button_box.set_name("BUTTON_COLOR")

	#def mouse_exit_view_packages	
			
	def mouse_over_update_button(self,widget,event):

		if not self.preactions_process_t.launched and not self.postactions_process_t.done:
			self.update_button_box.set_name("BUTTON_OVER_COLOR")
		else:
		 	if self.preactions_process_t.launched and not self.postactions_process_t.done :
		 		self.terminal_label.set_name("BLUE_FONT")
				self.terminal_label.set_markup(self.msg_upgrade_running)

	#def mouse_over_update_button
			
	def mouse_exit_update_button(self,widget,event):

		if self.preactions_process_t.launched and not self.postactions_process_t.done:
			self.terminal_label.set_name("CHANGELOG_FONT")
			self.terminal_label.set_markup(self.msg_terminal)
		else:
			if not self.preactions_process_t.launched:
				self.update_button_box.set_name("BUTTON_COLOR")

	#def mouse_exit_update_button
			
	def mouse_over_cancel(self,widget,event):

		self.cancel_button_box.set_name("BUTTON_OVER_COLOR")	

	#def mouse_over_cancel	

	def mouse_exit_cancel(self,widget,event):

		self.cancel_button_box.set_name("BUTTON_COLOR")	

	#def mouse_exit_cancel

	def mouse_over_return_arrow(self,widget,event):

		self.return_arrow_box.set_name("BUTTON_OVER_COLOR")	

	#def mouse_over_return_arrow	

	def mouse_exit_return_arrow(self,widget,event):

		self.return_arrow_box.set_name("BUTTON_COLOR")		

	#def mouse_exit_return_arrow	

	def show_indicator_switch (self):

		indicator=True

		try:
			if self.targetMetapackage !=None:
				if self.targetMetapackage =='lliurex-meta-client': 
					indicator=False
			else:
				if 'client' in self.llxup_connect.previousFlavours:
					indicator=False

			if indicator: 		
				self.indicator_box.show()

		except Exception as e:	
			self.indicator_box.hide()	

	#def show_indicator_switch		

	def config_indicator(self):

		show_indicator=self.indicator_switch.get_state()
		
		if show_indicator:
			if os.path.exists(DISABLE_INDICATOR_TOKEN):
				os.remove(DISABLE_INDICATOR_TOKEN)
		else:
			if not os.path.exists(DISABLE_INDICATOR_TOKEN):
				if not os.path.exists(DISABLE_INDICATOR_PATH):
					os.mkdir(DISABLE_INDICATOR_PATH)
			
				f=open(DISABLE_INDICATOR_TOKEN,'w')
				f.close


	#def config_indicator			
				
	def quit(self,widget,event=None):

		self.llxup_connect.cleanEnvironment()
		self.llxup_connect.cleanLliurexUpLock()
		self.config_indicator()
		Gtk.main_quit()	

	#def quit	

#class LliurexUp

lup=LliurexUp()
#lup.start_gui()		
 
