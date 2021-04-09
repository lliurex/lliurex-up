#!/usr/bin/env python3


import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Pango, GdkPixbuf, Gdk, Gio, GObject,GLib,Gdk

import os

import Core
import settings
#from . import settings
import gettext
gettext.textdomain(settings.TEXT_DOMAIN)
_ = gettext.gettext

DISABLE_INDICATOR_PATH="/etc/lliurex-up-indicator"
DISABLE_INDICATOR_TOKEN=os.path.join(DISABLE_INDICATOR_PATH,'disableIndicator.token')


class PreferencesBox(Gtk.VBox):
	
	def __init__(self):
		
		Gtk.VBox.__init__(self)
		
		self.core=Core.Core.get_core()

		builder=Gtk.Builder()
		builder.set_translation_domain(settings.TEXT_DOMAIN)

		ui_path=self.core.ui_path
		builder.add_from_file(ui_path)

	
		self.main_box=builder.get_object("preferences_box")
		self.preferences_label=builder.get_object("preferences_label")
		self.systray_box=builder.get_object("systray_box")
		self.systray_label=builder.get_object("systray_label")
		self.systray_switch=builder.get_object("systray_switch")
		self.systray_switch.connect("notify::active", self.config_systray)
		self.pack_start(self.main_box,True,True,0)

		if os.path.exists(DISABLE_INDICATOR_TOKEN):
			self.systray_switch.set_active(True)
		else:
			self.systray_switch.set_active(False)

				
	#def __init__
	
	def show_systray_switch (self):

		systray=True

		try:
			if self.core.llxUpConnect.targetMetapackage !=None:
				#if self.targetMetapackage =='lliurex-meta-client' or self.targetMetapackage=='lliurex-meta-minimal-client': 
				if self.core.llxUpConnect.search_meta('client'):
					systray=False
									
			else:
				#if 'client' in self.llxup_connect.previousFlavours or 'minimal-client' in self.llxup_connect.previousFlavours:
				if self.core.llxUpConnect.search_meta('client'):	
					systray=False

			if systray: 		
				self.systray_box.show()

		except Exception as e:	
			self.systray_box.hide()	

	#def show_systray_switch		

	def config_systray(self,switch,gparam):

		if not switch.get_active():
			if os.path.exists(DISABLE_INDICATOR_TOKEN):
				os.remove(DISABLE_INDICATOR_TOKEN)
		else:
			if not os.path.exists(DISABLE_INDICATOR_TOKEN):
				if not os.path.exists(DISABLE_INDICATOR_PATH):
					os.mkdir(DISABLE_INDICATOR_PATH)
			
				f=open(DISABLE_INDICATOR_TOKEN,'w')
				f.close()


	#def config_systray		
	
		
#class PreferencesBox

#from . import Core