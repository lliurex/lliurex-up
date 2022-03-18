#!/usr/bin/env python3


import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Pango, GdkPixbuf, Gdk, Gio, GObject,GLib,Gdk

import os
import configparser
import copy
import time
import threading

import Core
import settings
import gettext
gettext.textdomain(settings.TEXT_DOMAIN)
_ = gettext.gettext




class PackagesBox(Gtk.VBox):
	
	def __init__(self):
		
		Gtk.VBox.__init__(self)
		
		self.core=Core.Core.get_core()
		
		builder=Gtk.Builder()
		builder.set_translation_domain(settings.TEXT_DOMAIN)

		ui_path=self.core.ui_path
		builder.add_from_file(ui_path)

		self.css_file=self.core.rsrc_dir+"lliurex-up.css"

		self.main_box=builder.get_object("packages_box")
		self.search_entry=builder.get_object("search_entry")
		self.search_entry.connect("changed",self.search_entry_changed)

		self.packages_list_box=builder.get_object("packages_list_box")
		self.list_box=builder.get_object("list_box")
		self.pack_start(self.main_box,True,True,0)

		self.stack_popover=Gtk.Stack()
		self.stack_popover.set_transition_duration(750)
		self.stack_popover.set_transition_type(Gtk.StackTransitionType.CROSSFADE)

		self.popover_changelog=builder.get_object("changelog_popover")
		self.changelog_main_box=builder.get_object("changelog_main_box")
		self.changelog_box=builder.get_object("changelog_box")
		self.changelog_tw=builder.get_object("changelog_tw")
		self.waiting_box=builder.get_object("waiting_box")
		self.waiting_spinner=builder.get_object("waiting_spinner")

		self.stack_popover.add_titled(self.waiting_box,"waitingBox","Waiting Box")
		self.stack_popover.add_titled(self.changelog_box,"changelogBox","Changelog Box")
		self.stack_popover.show_all()
		self.changelog_main_box.pack_start(self.stack_popover,True,True,5)
		
		self.search_list=[]
		self.packages_list=[]
		self.main_box.show_all()

		self.set_css_info()
		
				
	#def __init__

	def init_threads(self):

		self.load_changelog_t=threading.Thread()
		self.load_changelog_t.daemon=True

	#def init_threads	

	def set_css_info(self):
		
		self.style_provider=Gtk.CssProvider()

		f=Gio.File.new_for_path(self.css_file)
		self.style_provider.load_from_file(f)

		Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),self.style_provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		self.packages_list_box.set_name("LIST_BOX")
		self.list_box.set_name("LIST_BOX")

	#def set-css_info
	
	def draw_pkg_list(self):

		self.info=copy.deepcopy(self.core.loadBox.packages)

		info=self.info
		self.total_packages=len(info)
		count=self.total_packages
		self.newpackages=0	
		for item in info:
			tmp=item.split(";")
			if len(tmp)>1:
				if tmp[3]==str(None):
					self.newpackages=int(self.newpackages)+1

				self.new_pkg_box(tmp[3],tmp[0],tmp[1],tmp[2],count)	
				self.packages_list.append(tmp[0])
				count-=1	

	#def draw_pkg_list
	
	def new_pkg_box(self,installed,name,version,size,count):

		main_hbox=Gtk.HBox()
		hbox_eb=Gtk.EventBox()
		hbox_eb.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)
		hbox_eb.connect("button-press-event", self.show_changelog,main_hbox)
		hbox_eb.connect("motion-notify-event", self.mouse_over)
		hbox_eb.connect("leave-notify-event", self.mouse_exit)

		hbox=Gtk.HBox()

		image=Gtk.HBox()
		icon=self.parse_desktop(installed,name)
		icon.set_margin_left(5)
		icon.set_margin_top(5)
		icon.set_margin_bottom(5)
		icon.set_halign(Gtk.Align.CENTER)
		icon.set_valign(Gtk.Align.CENTER)
		icon.id=name
		icon.version=version
		icon.status=False
		image.pack_start(icon,True,True,5)

		vbox_pkg=Gtk.VBox()
		hbox_pkg_data=Gtk.HBox()
		hbox_pkg_name=Gtk.VBox()
		pkg_name=Gtk.Label()
		pkg_name.set_text(name)
		pkg_name.set_margin_left(10)
		pkg_name.set_margin_right(5)
		pkg_name.set_margin_top(5)
		pkg_name.set_margin_bottom(0)
		pkg_name.set_width_chars(40)
		pkg_name.set_xalign(-1)
		pkg_name.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
		pkg_name.set_name("PKG_NAME")
		pkg_name.id=name
		pkg_name.version=version
		pkg_name.status=False

		pkg_version=Gtk.Label()
		pkg_version.set_text(version)
		pkg_version.set_margin_left(10)
		pkg_version.set_margin_right(5)
		pkg_version.set_margin_top(0)
		pkg_version.set_margin_bottom(5)
		pkg_version.set_width_chars(40)
		pkg_version.set_xalign(-1)
		pkg_version.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
		pkg_version.id=name
		pkg_version.version=version
		pkg_version.status=False

		hbox_pkg_name.pack_start(pkg_name,False,False,0)
		hbox_pkg_name.pack_end(pkg_version,False,False,0)
		hbox_pkg_name.set_valign(Gtk.Align.CENTER)
		pkg_size=Gtk.Label()
		pkg_size.set_text(size)
		pkg_size.set_margin_right(15)
		pkg_size.set_margin_top(0)
		pkg_size.set_margin_bottom(0)
		pkg_size.set_width_chars(10)
		pkg_size.set_max_width_chars(10)
		pkg_size.set_xalign(1)
		pkg_size.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
		pkg_size.set_name("PKG_NAME")
		pkg_size.id=name
		pkg_size.version=version
		pkg_size.status=False

		state=Gtk.Image.new_from_file(os.path.join(settings.RSRC_DIR,"ok.png"))
		state.set_halign(Gtk.Align.CENTER)
		state.set_valign(Gtk.Align.CENTER)
		state.set_margin_left(5)
		state.set_margin_right(15)
		state.id=name
		state.version=version
		state.status=True
		state.hide()

		hbox_pkg_data.pack_start(hbox_pkg_name,False,False,0)
		hbox_pkg_data.pack_end(state,False,False,0)
		hbox_pkg_data.pack_end(pkg_size,False,False,0)
		hbox_pkg_data.set_valign(Gtk.Align.CENTER)
		
		list_separator=Gtk.Separator()
		list_separator.set_margin_left(10)
		list_separator.set_margin_right(15)

		if count!=1:
			list_separator.set_name("SEPARATOR")
		else:
			list_separator.set_name("WHITE_SEPARATOR")

		vbox_pkg.pack_start(hbox_pkg_data,False,False,5)
		vbox_pkg.pack_end(list_separator,False,False,0)

		vbox_pkg.set_valign(Gtk.Align.CENTER)
		hbox.pack_start(image,False,False,0)
		hbox.pack_start(vbox_pkg,True,True,0)
		hbox.show_all()
		hbox_eb.add(hbox)
		main_hbox.add(hbox_eb)
		main_hbox.show_all()
		main_hbox.set_halign(Gtk.Align.FILL)

		self.list_box.pack_start(main_hbox,False,False,0)
		self.list_box.queue_draw()
		self.list_box.set_valign(Gtk.Align.FILL)
		state.hide()
		main_hbox.queue_draw()	

	#def new_pkg_box

	def parse_desktop(self,installed,name):

		installed_icon=False
		desktop_file=os.path.join(settings.DESKTOP_PATH,name+".desktop")

		try:
			if str(installed)=='None':
				icon=os.path.join(settings.RSRC_DIR,"new_package.png")

			else:	
				config = configparser.ConfigParser()
				config.optionxform=str

				config.read(desktop_file)
				
				#Zomandos may include a desktop file of type zomando with info for the store. Those desktops must be skipped
				if config.has_section("Desktop Entry") and config.has_option("Desktop Entry","Icon") and config.get("Desktop Entry","Type").lower()!="zomando":
					icon=config.get("Desktop Entry","Icon")
					installed_icon=True
					icon_extension=os.path.splitext(icon)[1]
					if icon_extension==".xpm":
						icon=os.path.join(settings.RSRC_DIR,"package.png")
						installed_icon=False
				else:
					icon=os.path.join(settings.RSRC_DIR,"package.png")
				
		except Exception as e:
			icon=os.path.join(settings.RSRC_DIR,"package.png")

		if installed_icon:
			img=Gtk.Image.new_from_icon_name(icon,Gtk.IconSize.DIALOG)
		else:
			image=Gtk.Image.new_from_file(icon)
			pixbuf=image.get_pixbuf()
			icon=pixbuf.scale_simple(48,48,GdkPixbuf.InterpType.BILINEAR)
			img=Gtk.Image.new_from_pixbuf(icon)
		
		return img
		
	#def parse_desktop

	def show_changelog(self,widget,event,hbox):

		for item in hbox:
			pkg=item.get_children()[0].get_children()[1].get_children()[0].get_children()[2].id

		
		self.load_changelog_t=threading.Thread(target=self.load_pkg_changelog,args=(pkg,))
		self.load_changelog_t.start()
		self.popover_changelog.set_position(Gtk.PositionType.BOTTOM)
		self.popover_changelog.set_relative_to(hbox)
		self.stack_popover.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
		self.stack_popover.set_visible_child_name("waitingBox")
		self.waiting_spinner.start()
		self.popover_changelog.show()

		GLib.timeout_add(100,self.pulsate_load_changelog)

	#def show_changelog

	def pulsate_load_changelog(self):

		if self.load_changelog_t.is_alive():
			return True

		else:
			self.waiting_spinner.stop()
			self.stack_popover.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
			self.stack_popover.set_visible_child_name("changelogBox")
			self.changelog_tw.get_buffer().set_text("".join(self.changelog))

	#def pulsate_load_changelog

	def load_pkg_changelog(self,args):

		self.changelog=self.core.llxUpConnect.getPackageChangelog(args)

	#def load_pkg_changelog	

	def mouse_over(self,widget,event=None):

		widget.set_name("MOUSE_OVER")

	#def mouse_over	

	def mouse_exit(self,widget,event=None):
		
		widget.set_name("MOUSE_EXIT")

	#def mouse_exit	

	def update_state_icon(self):

		packages_status=self.core.llxUpConnect.getStatusPackage()

		for hbox in self.list_box.get_children():
			for item in hbox:
				name=item.get_children()[0].get_children()[1].get_children()[0].get_children()[2].id
				version=item.get_children()[0].get_children()[1].get_children()[0].get_children()[2].version
				pkg_name=name+"_"+version
				if pkg_name not in packages_status:
					item.get_children()[0].get_children()[1].get_children()[0].get_children()[2].set_from_file(os.path.join(settings.RSRC_DIR,"error.png"))

				item.get_children()[0].get_children()[1].get_children()[0].get_children()[2].show()

	#def update_state_icon

	def hide_non_search(self):

		for hbox in self.list_box.get_children():
			for item in hbox:
				name=item.get_children()[0].get_children()[1].get_children()[0].get_children()[2].id
				if name in self.search_list:
					hbox.hide()
				else:
					hbox.show()
	
	#def hide_non_search	

	def search_entry_changed(self,widget):

		self.search_list=[]
		search=self.search_entry.get_text().lower()
		tmp_pkg=copy.deepcopy(self.packages_list)

		if search=="":
			self.hide_non_search()
		else:
			for item in range(len(tmp_pkg)-1,-1,-1):
				pkg_name=tmp_pkg[item]
				if search in pkg_name:
					pass
				else:
					self.search_list.append(pkg_name)
					tmp_pkg.pop(item)

			if len(self.search_list)>0:
				self.hide_non_search()

	#search_entry_changed
		
#class PackageBox

#from . import Core