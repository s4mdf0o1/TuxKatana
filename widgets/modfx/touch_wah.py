import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

from widgets.slider import Slider
from widgets.toggle import Toggle
from widgets.box_inner import BoxInner

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

class TouchWahUI(Gtk.Box):
    def __init__(self, own_ctrl):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.own_ctrl = own_ctrl
        
        box_eff = BoxInner("Effect")
        self.filter_sw = Toggle("Low/Pass Band")
        self.filter_sw.name = "tw_filt_sw"
        self.own_ctrl.bind_property(
            "tw_filt_sw", self.filter_sw,
            "active", GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )
        box_eff.append(self.filter_sw)

        self.polar_sw = Toggle("Up/Down Polar")
        self.polar_sw.name = "tw_polar_sw"
        self.own_ctrl.bind_property(
            "tw_polar_sw", self.polar_sw,
            "active", GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )
        box_eff.append(self.polar_sw)

        box_tw = BoxInner("Touch Wah")
        self.peak_lvl = Slider( "Peak", "normal", self.own_ctrl, "tw_peak_lvl" )
        box_tw.append(self.peak_lvl)

        self.sens_lvl = Slider( "Sens", "normal", self.own_ctrl, "tw_sens_lvl" )
        box_tw.append(self.sens_lvl)

        self.freq_lvl = Slider( "Freq", "normal", self.own_ctrl, "tw_freq_lvl" )
        box_tw.append(self.freq_lvl)

        box_lvl = BoxInner("Level")

        self.eff_lvl = Slider( "Effect", "normal", self.own_ctrl, "tw_eff_lvl" )
        box_lvl.append(self.eff_lvl)

        self.dmix_lvl = Slider( "Direct Mix", "normal", self.own_ctrl, "tw_dmix_lvl" )
        box_lvl.append(self.dmix_lvl)

        self.append(box_eff)
        self.append(box_tw)
        self.append(box_lvl)

