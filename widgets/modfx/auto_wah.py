import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

from widgets.slider import Slider
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

        self.freq_lvl = Slider( "Freq", "normal", self.own_ctrl, "aw_freq_lvl" )
        box_aw.append(self.freq_lvl)

        self.peak_lvl = Slider( "Peak", "normal", self.own_ctrl, "aw_peak_lvl" )
        box_aw.append(self.peak_lvl)

        self.rate_lvl = Slider( "Rate", "normal", self.own_ctrl, "aw_rate_lvl" )
        box_aw.append(self.rate_lvl)

        self.depth_lvl = Slider( "Depth", "normal", self.own_ctrl, "aw_depth_lvl" )
        box_aw.append(self.depth_lvl)

        box_lvl = BoxInner("Level")

        self.eff_lvl = Slider( "Effect", "normal", self.own_ctrl, "aw_eff_lvl" )
        box_lvl.append(self.eff_lvl)

        self.dmix_lvl = Slider( "Direct Mix", "normal", self.own_ctrl, "aw_dmix_lvl" )
        box_lvl.append(self.dmix_lvl)

        self.append(box_eff)
        self.append(box_aw)
        self.append(box_lvl)

