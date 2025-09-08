import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

from .slider import Slider
from .bank import Bank
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from ruamel.yaml import YAML
yaml = YAML(typ="rt")
#with open("params/amplifier.yaml", 'r') as f:
#    params = yaml.load(f)
from .toggle import Toggle

class Amplifier(Gtk.Box):
    def __init__(self, ctrl):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.ctrl = ctrl
        self.own_ctrl = self.ctrl.device.amplifier

        self.amp_store = Gtk.ListStore(int, str, str)
        #self.amp_type = Gtk.ComboBoxText()
        #self.amp_type.name = "amp_num"
        #for t in ["Acoustic", "Clean", "Crunch", "Lead", "Brown"]:
        #    self.amp_type.append_text(t)
        self.amp_bank = Bank("TYPES", {
            "Acoustic": "SysEx:1,", 
            "Clean":    "SysEx:2",
            "Crunch":   "SysEx:3", 
            "Lead":     "SysEx:4",
            "Brown":    "SysEx:5" }, ctrl)
        self.append(self.amp_bank)
        self.own_ctrl.bind_property(
            "amp_num", self.amp_bank, "selected",
            GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE)

        
        self.amp_types = Gtk.ComboBox.new_with_model(self.amp_store)
        renderer = Gtk.CellRendererText()
        self.amp_types.pack_start(renderer, True)
        self.amp_types.add_attribute(renderer, "text", 1)  # colonne 0 = nom affiché

        self.own_ctrl.bind_property(
                "amp_type", self.amp_types, "active", 
                GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.BIDIRECTIONAL )
        #self.own_ctrl.bind_property(
        #        "amp_num", self.amp_types, "active", 
        #        GObject.BindingFlags.SYNC_CREATE  | GObject.BindingFlags.BIDIRECTIONAL)

        self.amp_types.connect("changed", self.on_combo_changed)
        self.append(self.amp_types)

        self.amp_variation = Toggle("Variation")
        self.amp_variation.name = "amp_variation"
        self.own_ctrl.bind_property(
                "amp_variation", self.amp_variation,
                "active", GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.BIDIRECTIONAL)
        self.amp_variation.connect("toggled", self.on_toggle_changed)
        self.append(self.amp_variation)

        self.amp_gain = Slider( "Gain", 50.0 )
        self.amp_gain.name = "amp_gain"
        self.own_ctrl.bind_property(
                "amp_gain", self.amp_gain,
                "value", GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.BIDIRECTIONAL )

        self.amp_gain.scale.connect("value-changed", self.on_slider_changed)
        self.append(self.amp_gain)

        self.amp_volume = Slider( "Volume", 50.0 )
        self.amp_volume.name = "amp_volume"
        self.own_ctrl.bind_property(
                "amp_volume", self.amp_volume,
                "value", GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.BIDIRECTIONAL )
        self.amp_volume.connect("value-changed", self.on_slider_changed)
        self.append(self.amp_volume)

        self.own_ctrl.connect("amp-types-loaded", self.on_amp_types_loaded)

    def on_combo_changed(self, combo):
        #log.debug(f"{self.amp_bank.find_property('selected').value}")
        idx = combo.get_active()
        log.debug(f"{idx=}")
        if idx >= 0:  # -1 si rien de sélectionné
            name, code = self.amp_store[idx][:2]
            log.debug(f"{self.amp_store[idx][:2]=}")
            #with self.own_ctrl.provenance("ui"):
            #self.own_ctrl.set_with_source("amp_type", code, "ui")
            self.own_ctrl.set_property("amp_type", idx)
        #log.debug(f"on_combo_changed: {self.amp_store[combo.get_active()]}")

    def on_slider_changed( self, slider):
        #with self.own_ctrl.provenance("ui"):
        #self.own_ctrl.set_with_source(slider.name, slider.get_value(), "ui")
        self.own_ctrl.set_property(slider.name, slider.get_value())

    def on_toggle_changed( self, toggle):
        #with self.own_ctrl.provenance("ui"):
        #self.own_ctrl.set_with_source(toggle.name, toggle.get_active(), "ui")
        self.own_ctrl.set_property(toggle.name, toggle.get_active())

    def on_amp_types_loaded(self, device, amp_types):
        #log.debug(f"Amplifier.on_amp_types_loaded: {amp_types}")
        #self.amp_store.remove_all()
        i = 0
        for name, code in amp_types.items():
            self.amp_store.append([i,name, code])
            i += 1

