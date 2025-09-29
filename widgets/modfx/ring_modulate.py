
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

from widgets.slider import Slider
from widgets.box_inner import BoxInner
from widgets.toggle import Toggle

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from lib.effect import Effect
from lib.set_mapping import add_properties

@add_properties()
class RingModulate(Effect, Gtk.Box):
    rm_norm_sw   = GObject.Property(type=bool, default=False)
    rm_freq_lvl     = GObject.Property(type=int, default=0)
    rm_effc_lvl     = GObject.Property(type=int, default=0)
    rm_dmix_lvl     = GObject.Property(type=int, default=0)

    def __init__(self, ctrl, pprefx=""):
        super().__init__(ctrl, self.mapping, pprefx)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(6)
        self.parent_prefix = pprefx

        box = BoxInner("Ring Modulate")
        self.append(box)

        self.norm = Toggle("Normal / Intelligent")
        self.bind_property(
            "rm_norm_sw", self.norm,
            "active", GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )
        box.append(self.norm)

        self.rm_freq = Slider( "Freq.", "normal", self, "rm_freq_lvl" )
        box.append(self.rm_freq)

        box = BoxInner("Level")
        self.append(box)

        self.rm_effc = Slider( "Effect", "normal", self, "rm_effc_lvl" )
        box.append(self.rm_effc)

        self.rm_dmix = Slider( "Direct Mix", "normal", self, "rm_dmix_lvl" )
        box.append(self.rm_dmix)


