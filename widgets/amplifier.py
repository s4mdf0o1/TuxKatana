import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

from .slider import Slider
import logging
dbg=logging.getLogger("debug")

class Amplifier(Gtk.Box):
    def __init__(self, ctrl):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.ctrl = ctrl

        self.amp_type = Gtk.ComboBoxText()
        self.amp_type.name = "amp_type"
        for t in ["Acoustic", "Clean", "Crunsh", "Lead", "Brown"]:
            self.amp_type.append_text(t)
        self.ctrl.device.bind_property( "amp_type", self.amp_type, \
                        "active", GObject.BindingFlags.SYNC_CREATE)
        self.amp_type.connect("changed", self.on_combo_changed)
        self.append(self.amp_type)

        self.amp_gain = Slider( "Gain" )
        self.amp_gain.name = "amp_gain"
        self.ctrl.device.bind_property("amp_gain", self.amp_gain, \
                       "value", GObject.BindingFlags.SYNC_CREATE)# | \
                       #GObject.BindingFlags.BIDIRECTIONAL)
        self.amp_gain.scale.connect("value-changed", self.on_slider_changed)
        self.append(self.amp_gain)

        self.amp_volume = Slider( "Volume" )
        self.amp_volume.name = "amp_volume"
        self.ctrl.device.bind_property("amp_volume", self.amp_volume, \
                       "value", GObject.BindingFlags.SYNC_CREATE)# | \
                       #GObject.BindingFlags.BIDIRECTIONAL)
        self.amp_volume.connect("value-changed", self.on_slider_changed)
        self.append(self.amp_volume)

        self.amp_variation = Gtk.ToggleButton(label="Variation")
        


    def on_combo_changed(self, combo):
        self.ctrl.device.set_param(combo.name, combo.get_active())

    def on_slider_changed( self, slider):
        self.ctrl.device.set_param(slider.name, slider.get_value())


        


