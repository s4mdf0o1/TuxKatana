import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

from .slider import Slider
from .bank import Bank
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

#from ruamel.yaml import YAML
#yaml = YAML(typ="rt")
from .toggle import Toggle

class Amplifier(Gtk.Box):
    def __init__(self, ctrl):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.ctrl = ctrl
        self.own_ctrl = self.ctrl.device.amplifier

        self.amp_store = Gtk.ListStore(int, str, str)
        bank_buttons = dict(list(self.own_ctrl.map['Models'].items())[:5])
        #log.debug(bank_buttons)
        self.amp_bank = Bank("TYPE", bank_buttons, ctrl)
        self.append(self.amp_bank)
        self.own_ctrl.bind_property(
            "amp_num", self.amp_bank, "selected",
            GObject.BindingFlags.BIDIRECTIONAL |\
            GObject.BindingFlags.SYNC_CREATE )

        self.amp_models = Gtk.ComboBox.new_with_model(self.amp_store)
        renderer = Gtk.CellRendererText()
        self.amp_models.pack_start(renderer, True)
        self.amp_models.add_attribute(renderer, "text", 1)

        self.own_ctrl.bind_property(
            "model_idx", self.amp_models, "active", 
            GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )

        self.amp_models.connect("changed", self.on_combo_changed)
        self.append(self.amp_models)

        self.amp_variation = Toggle("Variation")
        self.amp_variation.name = "amp_variation"
        self.own_ctrl.bind_property(
            "amp_variation", self.amp_variation,
            "active", GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )
        self.amp_variation.connect("toggled", self.on_toggle_changed)
        self.append(self.amp_variation)

        self.amp_gain = Slider( "Gain", 50.0, self.own_ctrl, "gain_lvl" )
        self.amp_gain.name = "gain_lvl"
#        self.own_ctrl.bind_property(
#            "amp_gain", self.amp_gain,
#            "value", GObject.BindingFlags.SYNC_CREATE |\
#            GObject.BindingFlags.BIDIRECTIONAL )

        self.amp_gain.scale.connect("value-changed", self.on_slider_changed)
        self.append(self.amp_gain)

        self.amp_volume = Slider( "Volume", 50.0, self.own_ctrl, 'volume_lvl' )
        self.amp_volume.name = "volume_lvl"
#        self.own_ctrl.bind_property(
#            "amp_volume", self.amp_volume,
#            "value", GObject.BindingFlags.SYNC_CREATE |\
#            GObject.BindingFlags.BIDIRECTIONAL )
        self.amp_volume.connect("value-changed", self.on_slider_changed)
        self.append(self.amp_volume)

        self.own_ctrl.connect("amp-map-ready", self.on_amp_models_loaded)

    def on_combo_changed(self, combo):
        idx = combo.get_active()
        if idx >= 0:  # -1 si rien de sélectionné
            name, code = self.amp_store[idx][:2]
            self.own_ctrl.set_property("model_idx", idx)

    def on_slider_changed( self, slider):
        self.own_ctrl.set_property(slider.name, slider.get_value())

    def on_toggle_changed( self, toggle):
        self.own_ctrl.set_property(toggle.name, toggle.get_active())

    def on_amp_models_loaded(self, device, amp_models):
        i = 0
        #log.debug(amp_models.items())
        for name, code in amp_models.items():
            self.amp_store.append([i,name, code])
            i += 1

