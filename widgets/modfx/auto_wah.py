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
class AutoWah(Effect, Gtk.Box):
    aw_filt_sw      = GObject.Property(type=bool, default=False)
    aw_freq_lvl     = GObject.Property(type=int, default=0)
    aw_peak_lvl     = GObject.Property(type=int, default=0)
    aw_rate_lvl     = GObject.Property(type=int, default=0)
    aw_depth_lvl    = GObject.Property(type=int, default=0)
    aw_eff_lvl      = GObject.Property(type=int, default=0)
    aw_dmix_lvl     = GObject.Property(type=int, default=0)
    def __init__(self, ctrl, pprefx=""):
        super().__init__(ctrl, self.mapping, pprefx)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(6)
        self.parent_prefix = pprefx
        
        box_eff = BoxInner("Effect")

        self.filter_sw = Toggle("Low/Band Filter")
        self.filter_sw.name = pprefx + "aw_filt_sw"
        self.bind_property(
            "aw_filt_sw", self.filter_sw,
            "active", GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )
        box_eff.append(self.filter_sw)

        box_aw = BoxInner("Auto Wah")

        self.freq_lvl = Slider( "Freq", "normal", self, "aw_freq_lvl" )
        box_aw.append(self.freq_lvl)

        self.peak_lvl = Slider( "Peak", "normal", self, "aw_peak_lvl" )
        box_aw.append(self.peak_lvl)

        self.rate_lvl = Slider( "Rate", "normal", self, "aw_rate_lvl" )
        box_aw.append(self.rate_lvl)

        self.depth_lvl = Slider( "Depth", "normal", self, "aw_depth_lvl" )
        box_aw.append(self.depth_lvl)

        box_lvl = BoxInner("Level")

        self.eff_lvl = Slider( "Effect", "normal", self, "aw_eff_lvl" )
        box_lvl.append(self.eff_lvl)

        self.dmix_lvl = Slider( "Direct Mix", "normal", self, "aw_dmix_lvl" )
        box_lvl.append(self.dmix_lvl)

        self.append(box_eff)
        self.append(box_aw)
        self.append(box_lvl)

