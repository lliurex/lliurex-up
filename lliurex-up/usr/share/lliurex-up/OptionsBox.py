#!/usr/bin/env python3


import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Pango, GdkPixbuf, Gdk, Gio, GObject,GLib,Gdk

import os
import sys
import pwd
import threading
import time
import Core
import settings
import gettext
gettext.textdomain(settings.TEXT_DOMAIN)
_ = gettext.gettext



class OptionsBox(Gtk.VBox):
	
	def __init__(self):
		
		Gtk.VBox.__init__(self)
		
		self.core=Core.Core.get_core()
		
		builder=Gtk.Builder()
		builder.set_translation_domain(settings.TEXT_DOMAIN)

		ui_path=self.core.ui_path
		builder.add_from_file(ui_path)

		self.css_file=self.core.rsrc_dir+"lliurex-up.css"

		self.stack = Gtk.Stack()
		self.stack.set_transition_duration(1000)
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
		
		self.main_box=builder.get_object("options_box")
		self.top_box=builder.get_object("top_box")
		self.menu_box=builder.get_object("menu_box")
		self.info_btn=builder.get_object("info_btn")
		self.pkgs_btn=builder.get_object("pkgs_btn")
		self.terminal_btn=builder.get_object("terminal_btn")
		self.preferences_btn=builder.get_object("preferences_btn")
		self.help_btn=builder.get_object("help_btn")

		
		self.informationBox=self.core.informationBox
		self.packagesBox=self.core.packagesBox
		self.terminalBox=self.core.terminalBox
		self.preferencesBox=self.core.preferencesBox
		
		self.stack.add_titled(self.informationBox,"information","Information")
		self.stack.add_titled(self.packagesBox,"packages", "Packages")
		self.stack.add_titled(self.terminalBox,"terminal", "Terminal")
		self.stack.add_titled(self.preferencesBox,"preferences", "Preferences")
		self.stack.show_all()

		self.top_box.pack_start(self.stack,True,True,5)
		self.connect_signals()
		self.top_box.show_all()
		self.pack_start(self.main_box,True,True,0)
		self.main_box.show_all()
		self.set_css_info()
		self.init_threads()

				
	#def __init__

	def set_css_info(self):
		
		self.style_provider=Gtk.CssProvider()

		f=Gio.File.new_for_path(self.css_file)
		self.style_provider.load_from_file(f)

		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		#self.systray_label.set_name("MSG_LABEL")
		self.info_btn.set_name("BORDERLESS_BUTTON")
		self.pkgs_btn.set_name("BORDERLESS_BUTTON")
		self.terminal_btn.set_name("BORDERLESS_BUTTON")
		self.preferences_btn.set_name("BORDERLESS_BUTTON")
		self.help_btn.set_name("BORDERLESS_BUTTON")
		self.menu_box.set_name("MENU_BOX")

	#def set-css_info

	def connect_signals(self):

		self.info_btn.connect("clicked",self.change_panel,"information")
		self.pkgs_btn.connect("clicked",self.change_panel,"packages")
		self.terminal_btn.connect("clicked",self.change_panel,"terminal")		
		self.preferences_btn.connect("clicked",self.change_panel,"preferences")
		self.help_btn.connect("clicked",self.help_clicked)

	#def connect_signals
	def init_threads(self):

		self.open_help_t=threading.Thread(target=self.open_help)
		self.open_help_t.daemon=True

	#def init_threads	


	def change_panel(self,widget,panel):

		if panel=="preferences":
			self.preferencesBox.confirmation_box.hide()
		self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
		self.stack.set_visible_child_name(panel)	
		self.stack.set_transition_duration(1000)

	#def change_panel


	def show_info_panel(self,hide,error,msg):

		self.show_preferences()
		self.core.preferencesBox.show_systray_switch()
		self.terminal_btn.set_sensitive(False)

		if hide:
			self.pkgs_btn.hide()
			self.terminal_btn.hide()
	
		self.informationBox.load_panel(hide,error,msg)
		self.stack.set_visible_child_name("information")
	
	#def show_info_panel	

	def show_preferences(self):

		preferences=True

		try:
			if self.core.llxUpConnect.targetMetapackage !=None:
				#if self.targetMetapackage =='lliurex-meta-client' or self.targetMetapackage=='lliurex-meta-minimal-client': 
				if self.core.llxUpConnect.search_meta('client'):
					preferences=False
									
			else:
				if self.core.llxUpConnect.search_meta('client'):	
					preferences=False

			if preferences: 		
				self.preferences_btn.show()
			else:
				self.preferences_btn.hide()	

		except Exception as e:	
			self.preferences_btn.hide()	

	#def show_preferences

	def help_clicked(self,widget):

		language=os.environ["LANGUAGE"]
		lang=os.environ["LANG"]
		run_pkexec=False
		
		if "PKEXEC_UID" in os.environ:
			run_pkexec=True
		
		exec_lang=""
		app_lang=""

		if language=="":
			app_lang=lang
		else:
			language=language.split(":")[0]
			app_lang=language

		if 'valencia' in app_lang:
			exec_lang="LANG=ca_ES.UTF-8@valencia"
			cmd=exec_lang +' xdg-open https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Lliurex+Up.'
		else:
			exec_lang="LANG=es_ES.UTF-8"
			cmd=exec_lang +' xdg-open https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Lliurex+Up'
		if not run_pkexec:
			self.fcmd="su -c '%s' $USER" %cmd
		else:
			user=pwd.getpwuid(int(os.environ["PKEXEC_UID"])).pw_name
			self.fcmd="su -c '" +cmd+ "' "+ user
			
		self.init_threads()
		self.open_help_t.start()

	#help_clicked		
	

	def open_help(self):

		os.system(self.fcmd)

	#def open_help	
	

	
#class OptionsBox


