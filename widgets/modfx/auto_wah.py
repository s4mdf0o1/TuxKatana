import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

# from .slider import Slider
from widgets.slider import Slider
# from .tabbed_panel import TabbedPanel
# from .bank import Bank
from widgets.toggle import Toggle
from widgets.box_inner import BoxInner

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

class AutoWahUI(Gtk.Box):
    def __init__(self, own_ctrl):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.own_ctrl = own_ctrl
        
        box_eff = BoxInner("Effect")

        self.filter_sw = Toggle("Low/Band Filter")
        self.filter_sw.name = "aw_filt_sw"
        self.own_ctrl.bind_property(
            "aw_filt_sw", self.filter_sw,
            "active", GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )
        box_eff.append(self.filter_sw)

        box_aw = BoxInner("Auto Wah")

        self.filt_lvl = Slider( "Filter", "normal", self.own_ctrl, "aw_peak_lvl" )
        self.filt_lvl.name = "aw_peak_lvl"
        self.filt_lvl.connect("delayed-value", self.on_slider_changed)
        box_aw.append(self.filt_lvl)

        self.freq_lvl = Slider( "Freq", "normal", self.own_ctrl, "aw_freq_lvl" )
        self.freq_lvl.name = "aw_freq_lvl"
        self.freq_lvl.connect("delayed-value", self.on_slider_changed)
        box_aw.append(self.freq_lvl)

        self.peak_lvl = Slider( "Peak", "normal", self.own_ctrl, "aw_peak_lvl" )
        self.peak_lvl.name = "aw_peak_lvl"
        self.peak_lvl.connect("delayed-value", self.on_slider_changed)
        box_aw.append(self.peak_lvl)

        self.rate_lvl = Slider( "Rate", "normal", self.own_ctrl, "aw_rate_lvl" )
        self.rate_lvl.name = "aw_rate_lvl"
        self.rate_lvl.connect("delayed-value", self.on_slider_changed)
        box_aw.append(self.rate_lvl)

        self.depth_lvl = Slider( "Depth", "normal", self.own_ctrl, "aw_depth_lvl" )
        self.depth_lvl.name = "aw_depth_lvl"
        self.depth_lvl.connect("delayed-value", self.on_slider_changed)
        box_aw.append(self.depth_lvl)

        box_lvl = BoxInner("Level")

        self.eff_lvl = Slider( "Effect", "normal", self.own_ctrl, "aw_eff_lvl" )
        self.eff_lvl.name = "aw_eff_lvl"
        self.eff_lvl.connect("delayed-value", self.on_slider_changed)
        box_lvl.append(self.eff_lvl)

        self.dmix_lvl = Slider( "Direct Mix", "normal", self.own_ctrl, "aw_dmix_lvl" )
        self.dmix_lvl.name = "aw_dmix_lvl"
        self.dmix_lvl.connect("delayed-value", self.on_slider_changed)
        box_lvl.append(self.dmix_lvl)

        self.append(box_eff)
        self.append(box_aw)
        self.append(box_lvl)

    def on_slider_changed( self, slider, value):
        old_val = self.own_ctrl.get_property(slider.name)
        value = int(value)
        # log.debug(f"{old_val} {value}")
        if value != old_val:
            self.own_ctrl.set_property(slider.name, int(value))


