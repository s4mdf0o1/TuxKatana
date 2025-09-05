import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

from .slider import Slider
import logging
dbg=logging.getLogger("debug")

from .toggle import Toggle

class Amplifier(Gtk.Box):
    def __init__(self, ctrl):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.ctrl = ctrl

        self.amp_type = Gtk.ComboBoxText()
        self.amp_type.name = "amp_num"
        for t in ["Acoustic", "Clean", "Crunsh", "Lead", "Brown"]:
            self.amp_type.append_text(t)

        self.ctrl.device.amplifier.bind_property(
                "amp_num", self.amp_type,
                "active", GObject.BindingFlags.SYNC_CREATE  )
        #self.ctrl.device.amplifier.bind_property(
        #        "type_name", self.amp_type,
        #        "text", GObject.BindingFlags.SYNC_CREATE  )


        self.amp_type.connect("changed", self.on_combo_changed)
        self.append(self.amp_type)

        self.amp_variation = Toggle("Variation")
        self.amp_variation.name = "amp_variation"
        self.ctrl.device.amplifier.bind_property(
                "amp_variation", self.amp_variation,
                "active", GObject.BindingFlags.SYNC_CREATE  )
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



    def on_combo_changed(self, combo):
        self.ctrl.device.amplifier.set_param(combo.name, combo.get_active())

    def on_slider_changed( self, slider):
        self.ctrl.device.amplifier.set_param(slider.name, slider.get_value())

    def on_toggle_changed( self, toggle):
        self.ctrl.device.amplifier.set_param(toggle.name, toggle.get_active())



        


