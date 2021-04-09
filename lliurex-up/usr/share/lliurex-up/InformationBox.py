#!/usr/bin/env python3


import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Pango, GdkPixbuf, Gdk, Gio, GObject,GLib,Gdk

import os

import Core
import settings
import gettext
gettext.textdomain(settings.TEXT_DOMAIN)
_ = gettext.gettext



class InformationBox(Gtk.VBox):
	
	def __init__(self):
		
		Gtk.VBox.__init__(self)
		
		self.core=Core.Core.get_core()
		
		builder=Gtk.Builder()
		builder.set_translation_domain(settings.TEXT_DOMAIN)

		ui_path=self.core.ui_path
		builder.add_from_file(ui_path)

		self.css_file=self.core.rsrc_dir+"lliurex-up.css"
		
		self.main_box=builder.get_object("information_box")
		self.info_grid=builder.get_object("info_grid")
		self.current_version_label=builder.get_object("current_version_label")
		self.current_version_info_label=builder.get_object("current_version_info_label")
		self.version_available_label=builder.get_object("version_available_label")
		self.version_available_info_label=builder.get_object("version_available_info_label")
		self.version_update_label=builder.get_object("version_update_label")
		self.version_update_info_label=builder.get_object("version_update_info_label")
		self.number_packages_label=builder.get_object("number_packages_label")
		self.number_packages_info_label=builder.get_object("number_packages_info_label")
		self.size_update_label=builder.get_object("size_update_label")
		self.size_update_info_label=builder.get_object("size_update_info_label")

		self.warning_box=builder.get_object("warning_box")
		self.warning_img_error=builder.get_object("warning_img_error")
		self.warning_img_ok=builder.get_object("warning_img_ok")

		self.warning_label=builder.get_object("warning_label")
		self.pack_start(self.main_box,True,True,0)


		self.set_css_info()
		
				
	#def __init__

	def set_css_info(self):
		
		self.style_provider=Gtk.CssProvider()

		f=Gio.File.new_for_path(self.css_file)
		self.style_provider.load_from_file(f)

		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
			
	#def set-css_info
	
	def load_panel(self,hide,error,msg):

		self.main_box.show_all()
		if hide:
			self.info_grid.hide()
			self.warning_box.show()
			if error:
				self.warning_box.set_name("ERROR_BOX")
				self.warning_img_error.show()
				self.warning_img_ok.hide()
			else:
				self.warning_box.set_name("INFORMATION_BOX")
				self.warning_img_error.hide()
				self.warning_img_ok.show()


			self.warning_label.set_text(msg)


		else:
			self.info_grid.show()
			self.warning_box.hide()	


	#def load_panel

	def get_update_summary(self):

		if self.core.loadBox.version_update["installed"]==None:
			self.current_version_info_label.set_text(_("Not available"))

		else:
			self.current_version_info_label.set_text(self.core.loadBox.version_update["installed"])


		if self.core.loadBox.version_available==None:
			if self.core.llxUpConnect.search_meta('client'):
				self.version_available_info_label.set_text(_("Not available for clients"))

			else:
				self.version_available_info_label.set_name("ERROR_FONT")
				self.version_available_info_label.set_text(_("Not available. Check conexion to lliurex.net"))

		else:
			self.version_available_info_label.set_text(self.core.loadBox.version_available)


		if self.core.loadBox.version_update["candidate"]==None:
			self.version_update_info_label.set_text(_("Not available"))

		else:
			self.version_update_info_label.set_text(self.core.loadBox.version_update["candidate"])

		self.number_pkg=len(self.core.loadBox.packages)
		self.number_packages_info_label.set_text(str(self.number_pkg)+ " ("  +str(self.core.packagesBox.newpackages)+ _(" new)"))

		self.size_update_info_label.set_text(self.core.loadBox.size_update)

	
	#def get_update_summary	
	
		
#class InformationBox
