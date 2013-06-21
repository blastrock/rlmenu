#!/usr/bin/env python2

from gi.repository import Gtk
from gi.repository import Gdk, GdkPixbuf
from gi.repository import Gio
from subprocess import Popen
from xdg import BaseDirectory, DesktopEntry
import re
import sys
import os
import gmenu

ICON_THEME = Gtk.IconTheme.get_default()

class MyWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        Gtk.Window.__init__(self, title="GMenu Example", application=app)

class MyApplication(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self)

    def do_activate(self):
        win = MyWindow(self)

    def do_startup(self):
        # start the application
        Gtk.Application.do_startup(self)

        # create a menu
        self.menu = Gtk.Menu()
        # append to the menu three options
        self.add_to_menu(gmenu.lookup_tree('applications.menu'))
        # set the menu as menu of the application
        self.menu.connect("selection-done", self.on_close, None)
        self.menu.popup(None,None,None,None,0,Gtk.get_current_event_time())

    def add_to_menu(self, gmenu_tree):
        for m in gmenu_tree.root.contents:
            if m.get_type() == gmenu.TYPE_DIRECTORY:

                item = self.append_menu_item(self.menu, m.get_name(), m.get_icon(), None)

                submenu = Gtk.Menu()
            
                for app in m.contents:
                    if app.get_type() == gmenu.TYPE_ENTRY:
                        sub_item = self.append_menu_item(submenu, app.get_name(), app.get_icon(), app.get_comment())
                        sub_item.connect("activate", self.on_execute, app)
                        sub_item.show()

                item.set_submenu(submenu)
                item.show()
                
            elif m.get_type() == gmenu.TYPE_SEPARATOR:
                separator = Gtk.SeparatorMenuItem.new()
                self.menu.append(separator)
                separator.show() 

            elif m.get_type() == gmenu.TYPE_ENTRY:
                item = self.append_menu_item(self.menu, m.get_name(), m.get_icon(), m.get_comment())
                item.connect("activate", self.on_execute, m)
                item.show()

    def create_menu_item(self, label, icon_name, comment):
        item = Gtk.ImageMenuItem(None)
        item.set_label(label)

        #if Gtk.gtk_version >= (2, 16, 0):
        #    item.props.always_show_image = True
            
        icon_pixbuf = self.get_pixbuf_icon(icon_name)
        item.set_image(Gtk.Image.new_from_pixbuf(icon_pixbuf))
        
        if comment is not None:
            item.set_tooltip_text(comment)
        return item

    def append_menu_item(self, menu, label, icon_name, comment):
        item = self.create_menu_item(label, icon_name, comment)
        menu.append(item)
        return item

    def get_pixbuf_icon(self, icon_value, size=24):
        if not icon_value:
            return None

        #~ if os.path.isabs(icon_value):
        if os.path.isfile(icon_value) and not os.path.isdir(icon_value):
            try:
                return GdkPixbuf.Pixbuf.new_from_file_at_size(icon_value, size, size)
            except glib.GError:
                print 'core.get_pixbuf_icon : gtk.gdk.pixbuf_new_from_file_at_size >> glib.GError'
                return None
                    
            icon_name = os.path.basename(icon_value)
        else:
            icon_name = icon_value

        if re.match(".*\.(png|xpm|svg)$", icon_name) is not None:
            icon_name = icon_name[:-4]
        try:
            return ICON_THEME.load_icon(icon_name, size, 0)
        except Exception as e:
            for dir in BaseDirectory.xdg_data_dirs:
                for i in ("pixmaps", "icons"):
                    path = os.path.join(dir, i, icon_value)
                    if os.path.isfile(path):
                        return GdkPixbuf.Pixbuf.new_from_file_at_size(path, size, size)
            
    def on_execute(self, widget, app):
        command = app.exec_info.split('%')[0]
        if app.launch_in_terminal:
            command = 'x-terminal-emulator -e %s' % command
        Popen(command, shell=True)

    def on_close(self, widget, arg):
        sys.exit(0)

app = MyApplication()
exit_status = app.run(sys.argv)
sys.exit(exit_status)
