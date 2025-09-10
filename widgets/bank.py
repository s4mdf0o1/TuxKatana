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

    def __init__(self, label, buttons, ctrl, single=False):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.get_style_context().add_class("inner")
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.single = single
        #self.single_list = []
        #grid = Gtk.Grid()
        #grid.set_column_homogeneous(True)
        label = Gtk.Label(label=label)
        self.append(label)
        self.append(box)
        #self.append(grid)
        self.ctrl = ctrl
        self.buttons = []
        for i, b in enumerate(buttons):
            button = Toggle( b, buttons[b] )
            button.handler_id = button.connect("toggled", self.on_toggled,i)
            button.set_hexpand(True)
            button.set_halign(Gtk.Align.FILL)
            self.buttons.append(button)
            box.append( button )
            #grid.attach( button, i, 0,1,1 )
        if not self.single:
            self.connect("notify::selected", self.on_selected)
        #else:
        #    self.connect("notify::single_list", self.on_update_list)

    def on_selected(self, obj, pspec):
        #log.debug(f"bank.on_selected({self.selected})")
        button = self.buttons[obj.selected]
        button.handler_block(button.handler_id)
        button.set_active(True)
        self.set_inactives(button)
        button.handler_unblock(button.handler_id)

#    def on_update_list(self, widget, value):
#        log.debug(f"{widget}, {value}")
            
    def on_toggled(self, widget, idx):
        #log.debug(f"{widget} {widget.get_active()}" )
        log.debug(f"{self.single=} {hasattr(self, 'f_bank')=}")
        if not self.single or hasattr(self, "f_bank"):
            self.selected = idx
            self.set_inactives( widget )
            if hasattr(self, "f_bank"):
                self.f_bank.set_inactives()
#        else:
#            if widget.get_active():
#                self.single_list.append(idx)
#            else:
#                self.single_list.pop(self.single_list.index(idx))
#            log.debug(self.single_list)
        #if hasattr(self, "f_bank"):
        #    self.f_bank.set_inactives()

    def set_inactives( self, widget=None ):
        for button in self.buttons:
            if button != widget and button.get_active():
                button.handler_block(button.handler_id)
                button.set_active(False)
                button.handler_unblock(button.handler_id)


