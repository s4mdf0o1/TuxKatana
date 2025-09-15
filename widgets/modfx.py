import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

from .slider import Slider
from .tabbed_panel import TabbedPanel
from .bank import Bank
from .toggle import Toggle
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)
from lib.tools import from_str, midi_str_to_int

class ModFxUI(Gtk.Box):
    def __init__(self, own_ctrl, name):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        #self.ctrl = ctrl
        #self.own_ctrl = self.ctrl.device.modfx
        self.own_ctrl = own_ctrl
        
        banks = {"GREEN":'1', "RED":'2', "YELLOW":'3'}
        self.bank_select = Bank(name, banks)
        self.bank_select.buttons[0].set_status_id(1)
        self.bank_select.buttons[2].set_status_id(3)
        self.append(self.bank_select)
        
        prefix = name.lower()
        self.own_ctrl.bind_property(
            prefix + "_select", self.bank_select, "selected",
            GObject.BindingFlags.BIDIRECTIONAL |\
            GObject.BindingFlags.SYNC_CREATE )

