import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

class TabbedPanel(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        self.stack = Gtk.Stack()
        self.stack.set_transition_duration(150)

        sidebar = Gtk.StackSidebar()
        sidebar.set_stack( self.stack )
        self.set_vexpand(True)

        self.append(sidebar)
        self.append(self.stack)

    def add_tab(self, widget, name, title):
        self.stack.add_titled(widget, name, title)

    def set_active_tab(self, name):
        self.stack.set_visible_child_name(name)


