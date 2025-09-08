import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GObject #GLib, Gdk

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from widgets.toggle import Toggle

class Bank(Gtk.Box):
    selected = GObject.Property(type=int, default=-1)
    def __init__(self, label, buttons, ctrl):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.get_style_context().add_class("inner")
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        label = Gtk.Label(label=label)
        self.append(label)
        self.append(box)
        self.ctrl = ctrl
        #self.selected = -1
        self.buttons = []
        for i, b in enumerate(buttons):
            button = Toggle( b, buttons[b] )
            button.handler_id = button.connect("toggled", self.on_toggled,i)
            self.buttons.append(button)
            box.append( button )
        self.connect("notify::selected", self.on_selected)

    def on_selected(self, obj, pspec):
        log.debug(f"bank.on_selected({self.selected})")
        button = self.buttons[obj.selected]
        button.handler_block(button.handler_id)
        button.set_active(True)
        self.set_inactives(button)
        button.handler_unblock(button.handler_id)
        #self.on_toggled(self.buttons[obj.selected], obj.selected)
            
    def on_toggled(self, widget, idx):
        #self.ctrl.set_on( widget.path )
        self.selected = idx
        self.set_inactives( widget )
        if hasattr(self, "f_bank"):
            self.f_bank.set_inactives()

    def set_inactives( self, widget=None ):
        for button in self.buttons:
            if button != widget and button.get_active():
                button.handler_block(button.handler_id)
                button.set_active(False)
                button.handler_unblock(button.handler_id)


