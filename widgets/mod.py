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

class ModFx(Gtk.Box):
    def __init__(self, ctrl, name):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.name = name
        self.prefix = name.lower()
        self.ctrl = ctrl
        self.own_ctrl = self.ctrl.device.modfx
        
        banks = {"GREEN":'1', "RED":'2', "YELLOW":'3'}
        self.bank_select = Bank(name, banks, ctrl)
        self.bank_select.buttons[0].set_status_id(1)
        self.bank_select.buttons[2].set_status_id(3)
        self.append(self.bank_select)
        
        self.own_ctrl.bind_property(
            prefix + "_select", self.bank_select, "selected",
            GObject.BindingFlags.BIDIRECTIONAL |\
            GObject.BindingFlags.SYNC_CREATE )

        box_sel = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        self.types_store = Gtk.ListStore(int, str, str)
        self.types = Gtk.ComboBox.new_with_model(self.types_store)
        self.types.set_hexpand(True)
        renderer = Gtk.CellRendererText()
        self.types.pack_start(renderer, True)
        self.types.add_attribute(renderer, "text", 1)
        self.own_ctrl.bind_property(
            self.prefix + "_type_idx", self.types, "active", 
            GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )
        box_sel.append(self.types)
        self.types.connect("changed", self.on_type_changed)
        self.append(box_sel)
 
        self.own_ctrl.connect(self.prefix + "-map-ready", self.on_modfx_loaded)

     def on_modfx_loaded(self, device, types):
        i = 0
        for name, code in types.items():
            self.types_store.append([i,name, code])
            i += 1
        i = 0

       
