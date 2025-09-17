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
class ReverbUI(Gtk.Box):
    def __init__(self, own_ctrl):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.own_ctrl = own_ctrl
        
        banks = {"GREEN":'1', "RED":'2', "YELLOW":'3'}
        self.bank_select = Bank("REVERB", banks)
        self.bank_select.buttons[0].set_status_id(1)
        self.bank_select.buttons[2].set_status_id(3)
        self.append(self.bank_select)

        self.own_ctrl.bind_property(
            "bank_select", self.bank_select, "selected",
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
            "type_idx", self.types, "active", 
            GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )
        box_sel.append(self.types)

        self.modes_store = Gtk.ListStore(int, str, str)
        self.modes = Gtk.ComboBox.new_with_model(self.modes_store)
        self.modes.set_hexpand(True)
        renderer = Gtk.CellRendererText()
        self.modes.pack_start(renderer, True)
        self.modes.add_attribute(renderer, "text", 1)
        self.own_ctrl.bind_property(
            "mode_idx", self.modes, "active", 
            GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )
        box_sel.append(self.modes)

        self.append(box_sel)

        box_revb = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        box_revb.get_style_context().add_class('inner')
        label=Gtk.Label(label="Reverb")
        label.set_xalign(1.0)
        label.set_margin_end(20)
        box_revb.append(label)

        self.pre_delay_lvl = Slider( "Pre Delay", "time_500ms", self.own_ctrl, "pre_delay_lvl" )
        self.pre_delay_lvl.name = "pre_delay_lvl"
        self.pre_delay_lvl.connect("delayed-value", self.on_slider_changed)
        box_revb.append(self.pre_delay_lvl)

        self.time_lvl = Slider( "Time", "time_10s", self.own_ctrl, "time_lvl" )
        self.time_lvl.name = "time_lvl"
        self.time_lvl.connect("delayed-value", self.on_slider_changed)
        box_revb.append(self.time_lvl)

        self.density_lvl = Slider( "Density", "density", self.own_ctrl, "density_lvl" )
        self.density_lvl.name = "density_lvl"
        self.density_lvl.connect("delayed-value", self.on_slider_changed)
        box_revb.append(self.density_lvl)

        self.append(box_revb)

        box_filt = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        box_filt.get_style_context().add_class('inner')
        label=Gtk.Label(label="Filter")
        label.set_xalign(1.0)
        label.set_margin_end(20)
        box_filt.append(label)

        self.low_cut_lvl = Slider( "Low Cut", "low_freq", self.own_ctrl, "low_cut_lvl" )
        self.low_cut_lvl.name = "low_cut_lvl"
        self.low_cut_lvl.connect("delayed-value", self.on_slider_changed)
        box_filt.append(self.low_cut_lvl)

        self.high_cut_lvl = Slider( "High Cut", "high_freq", self.own_ctrl, "high_cut_lvl" )
        self.high_cut_lvl.name = "high_cut_lvl"
        self.high_cut_lvl.connect("delayed-value", self.on_slider_changed)
        box_filt.append(self.high_cut_lvl)

        self.append(box_filt)

        box_lvl = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        box_lvl.get_style_context().add_class('inner')
        label=Gtk.Label(label="Level")
        label.set_xalign(1.0)
        label.set_margin_end(20)
        box_lvl.append(label)

        self.effect_lvl = Slider( "Effect", "normal", self.own_ctrl, "effect_lvl" )
        self.effect_lvl.name = "effect_lvl"
        self.effect_lvl.connect("delayed-value", self.on_slider_changed)
        box_lvl.append(self.effect_lvl)

        self.dir_mix_lvl = Slider( "Direct Mix", "normal", self.own_ctrl, "dir_mix_lvl" )
        self.dir_mix_lvl.name = "dir_mix_lvl"
        self.dir_mix_lvl.connect("delayed-value", self.on_slider_changed)
        box_lvl.append(self.dir_mix_lvl)

        self.append(box_lvl)


        self.own_ctrl.connect("reverb-map-ready", self.on_reverb_loaded)

    def on_slider_changed( self, slider, value):
        old_val = self.own_ctrl.get_property(slider.name)
        value = int(value)
        # log.debug(f"{old_val} {value}")
        if value != old_val:
            self.own_ctrl.set_property(slider.name, value)

    def on_reverb_loaded(self, device, types, modes):
        i = 0
        for name, code in types.items():
            self.types_store.append([i,name, code])
            i += 1
        i = 0
        for name, code in modes.items():
            self.modes_store.append([i,name, code])
            i += 1


