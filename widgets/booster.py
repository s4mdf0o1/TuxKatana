import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

from .slider import Slider
from .tabbed_panel import TabbedPanel
from .bank import Bank
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

#from ruamel.yaml import YAML
#yaml = YAML(typ="rt")
#from .toggle import Toggle

class Booster(Gtk.Box):
    def __init__(self, ctrl):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.ctrl = ctrl
        self.own_ctrl = self.ctrl.device.booster
        banks = {"GREEN":'1', "RED":'2', "YELLOW":'3'}
        self.booster_bank = Bank("BANKS", banks, ctrl)
        self.booster_bank.buttons[0].set_status_id(1)
        self.booster_bank.buttons[2].set_status_id(3)
        self.append(self.booster_bank)
        self.own_ctrl.bind_property(
            "booster_bank", self.booster_bank, "selected",
            GObject.BindingFlags.BIDIRECTIONAL |\
            GObject.BindingFlags.SYNC_CREATE )

        self.booster_store = Gtk.ListStore(int, str, str)
        self.booster_types = Gtk.ComboBox.new_with_model(self.booster_store)
        renderer = Gtk.CellRendererText()
        self.booster_types.pack_start(renderer, True)
        self.booster_types.add_attribute(renderer, "text", 1)
        self.append(self.booster_types)
        self.own_ctrl.bind_property(
            "booster_num", self.booster_types, "active", 
            GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )

        self.booster_driver = Slider( "Driver", 50.0 )
        self.booster_driver.name = "booster_driver"
        self.own_ctrl.bind_property(
            "booster_driver", self.booster_driver,
            "value", GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )
        self.booster_driver.connect("value-changed", self.on_slider_changed)
        self.append(self.booster_driver)


        self.own_ctrl.connect("booster-loaded", self.on_booster_types_loaded)
        #self.booster_types_load(self, self.ctrl.device, self.own_ctrl.map['Types']['Codes'])

    def on_slider_changed( self, slider):
        self.own_ctrl.set_property(slider.name, slider.get_value())



    def on_booster_types_loaded(self, device, booster_types):
        i = 0
        for name, code in booster_types.items():
            self.booster_store.append([i,name, code])
            i += 1


