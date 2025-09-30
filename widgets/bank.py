import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GObject

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from widgets.toggle import Toggle

class Bank(Gtk.Box):
    selected = GObject.Property(type=int, default=-1)
    single_list = GObject.Property(type=object)

    def __init__(self, label, buttons, single=False, color_sw=False):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.get_style_context().add_class("inner")
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.single = single
        if label:
            label = Gtk.Label(label=label)
            self.append(label)
        self.append(box)
        self.buttons = []
        for i, name in enumerate(buttons):
            if name != 'DELAY_R':
                but = Toggle( name, buttons[name] )
                but.handler_id = but.connect("toggled", self.on_toggled,i)
                but.set_hexpand(True)
                but.set_halign(Gtk.Align.FILL)
                self.buttons.append(but)
                box.append( but )
        if not self.single:
            self.connect("notify::selected", self.on_selected)

    def on_selected(self, obj, pspec):
        #log.debug(f"bank.on_selected({self.selected})")
        button = self.buttons[obj.selected]
        button.handler_block(button.handler_id)
        button.set_active(True)
        self.set_inactives(button)
        button.handler_unblock(button.handler_id)

           
    def on_toggled(self, widget, idx):
        # log.debug(f"{widget.name}: {widget.get_active()}" )
        if not self.single or hasattr(self, "f_bank"):
            self.set_property("selected", idx)
            self.set_inactives( widget )
            if hasattr(self, "f_bank"):
                self.f_bank.set_inactives()

    def set_inactives( self, widget=None ):
        for button in self.buttons:
            if button != widget and button.get_active():
                button.handler_block(button.handler_id)
                button.set_active(False)
                button.handler_unblock(button.handler_id)


