import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

from .slider import Slider
import logging
dbg=logging.getLogger("debug")

from ruamel.yaml import YAML
yaml = YAML(typ="rt")
#with open("params/amplifier.yaml", 'r') as f:
#    params = yaml.load(f)
from .toggle import Toggle

class Amplifier(Gtk.Box):
    def __init__(self, ctrl):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.ctrl = ctrl

        self.amp_store = Gtk.ListStore(str, str)
        #self.amp_type = Gtk.ComboBoxText()
        #self.amp_type.name = "amp_num"
        #for t in ["Acoustic", "Clean", "Crunch", "Lead", "Brown"]:
        #    self.amp_type.append_text(t)
        self.amp_types = Gtk.ComboBox.new_with_model(self.amp_store)
        renderer = Gtk.CellRendererText()
        self.amp_types.pack_start(renderer, True)
        self.amp_types.add_attribute(renderer, "text", 0)  # colonne 0 = nom affiché

        self.ctrl.device.amplifier.bind_property(
                "amp_type", self.amp_types, "active_id", 
                GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.BIDIRECTIONAL )
        self.ctrl.device.amplifier.bind_property(
                "amp_num", self.amp_types, "active", 
                GObject.BindingFlags.SYNC_CREATE  | GObject.BindingFlags.BIDIRECTIONAL)

        self.amp_types.connect("changed", self.on_combo_changed)
        self.append(self.amp_types)

        self.amp_variation = Toggle("Variation")
        self.amp_variation.name = "amp_variation"
        self.ctrl.device.amplifier.bind_property(
                "amp_variation", self.amp_variation,
                "active", GObject.BindingFlags.SYNC_CREATE)# | GObject.BindingFlags.BIDIRECTIONAL)
        self.amp_variation.connect("toggled", self.on_toggle_changed)
        self.append(self.amp_variation)

        self.amp_gain = Slider( "Gain", 50.0 )
        self.amp_gain.name = "amp_gain"
        self.ctrl.device.amplifier.bind_property(
                "amp_gain", self.amp_gain,
                "value", GObject.BindingFlags.SYNC_CREATE  )

        self.amp_gain.scale.connect("value-changed", self.on_slider_changed)
        self.append(self.amp_gain)

        self.amp_volume = Slider( "Volume", 50.0 )
        self.amp_volume.name = "amp_volume"
        self.ctrl.device.amplifier.bind_property(
                "amp_volume", self.amp_volume,
                "value", GObject.BindingFlags.SYNC_CREATE  )
        self.amp_volume.connect("value-changed", self.on_slider_changed)
        self.append(self.amp_volume)

        self.ctrl.device.amplifier.connect("amp-types-loaded", self.on_amp_types_loaded)

    def on_combo_changed(self, combo):
        idx = combo.get_active()
        if idx >= 0:  # -1 si rien de sélectionné
            name, code = self.amp_store[idx][:2]
            self.ctrl.device.amplifier.set_amp_type(name, code)
        dbg.debug(f"on_combo_changed: {self.amp_store[combo.get_active()]}")

    def on_slider_changed( self, slider):
        self.ctrl.device.amplifier.set_param(slider.name, slider.get_value())

    def on_toggle_changed( self, toggle):
        self.ctrl.device.amplifier.set_param(toggle.name, toggle.get_active())


    def on_amp_types_loaded(self, device, amp_types):
        #dbg.debug(f"Amplifier.on_amp_types_loaded: {amp_types}")
        #self.amp_store.remove_all()
        for name, code in amp_types.items():
            self.amp_store.append([name, code])


        


