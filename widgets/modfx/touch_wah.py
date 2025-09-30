import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

from widgets.slider import Slider
from widgets.toggle import Toggle
from widgets.box_inner import BoxInner

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from lib.effect import Effect
from lib.set_mapping import add_properties

@add_properties()
class TouchWah(Effect, Gtk.Box):
    tw_filt_sw      = GObject.Property(type=bool, default=False)
    tw_polar_sw     = GObject.Property(type=bool, default=False)
    tw_peak_lvl     = GObject.Property(type=float, default=0.0)
    tw_sens_lvl     = GObject.Property(type=float, default=0.0)
    tw_freq_lvl     = GObject.Property(type=float, default=0.0)
    tw_eff_lvl      = GObject.Property(type=float, default=0.0)
    tw_dmix_lvl     = GObject.Property(type=float, default=0.0)

    def __init__(self, ctrl, pprefx=""):
        super().__init__(ctrl, self.mapping, pprefx)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(6)
        self.parent_prefix = pprefx
        
        box_eff = BoxInner("Effect")
        self.filter_sw = Toggle("Low/Pass Band")
        self.bind_property(
            "tw_filt_sw", self.filter_sw,
            "active", GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )
        box_eff.append(self.filter_sw)

        self.polar_sw = Toggle("Up/Down Polar")
        self.polar_sw.name = pprefx + "tw_polar_sw"
        self.bind_property(
            "tw_polar_sw", self.polar_sw,
            "active", GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )
        box_eff.append(self.polar_sw)

        box_tw = BoxInner("Touch Wah")
        self.peak_lvl = Slider( "Peak", "normal", self, "tw_peak_lvl" )
        box_tw.append(self.peak_lvl)

        self.sens_lvl = Slider( "Sens", "normal", self, "tw_sens_lvl" )
        box_tw.append(self.sens_lvl)

        self.freq_lvl = Slider( "Freq", "normal", self, "tw_freq_lvl" )
        box_tw.append(self.freq_lvl)

        box_lvl = BoxInner("Level")

        self.eff_lvl = Slider( "Effect", "normal", self, "tw_eff_lvl" )
        box_lvl.append(self.eff_lvl)

        self.dmix_lvl = Slider( "Direct Mix", "normal", self, "tw_dmix_lvl" )
        box_lvl.append(self.dmix_lvl)

        self.append(box_eff)
        self.append(box_tw)
        self.append(box_lvl)

