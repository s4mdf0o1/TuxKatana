
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
class Dc30(Effect, Gtk.Box):
    dc_selc_sw      = GObject.Property(type=bool, default=False)
    dc_cint_lvl     = GObject.Property(type=int, default=0)
    dc_inpt_lvl     = GObject.Property(type=int, default=0)
    dc_tone_lvl     = GObject.Property(type=int, default=0)
    dc_outd_sw      = GObject.Property(type=bool, default=False)
    dc_rept_lvl     = GObject.Property(type=int, default=0)
    dc_ints_lvl     = GObject.Property(type=int, default=0)
    dc_volm_lvl     = GObject.Property(type=int, default=0)

    def __init__(self, ctrl, pprefx=""):
        super().__init__(ctrl, self.mapping, pprefx)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(6)
        self.parent_prefix = pprefx

        box = BoxInner("DC30")
        self.append(box)

        self.dc_selc = Toggle("Chorus / Echo")
        self.bind_property(
            "dc_selc_sw", self.dc_selc,
            "active", GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )
        box.append(self.dc_selc)

        self.dc_cint = Slider( "Chorus Intens.", "normal", self, "dc_cint_lvl" )
        box.append(self.dc_cint)

        box = BoxInner("Settings")
        self.append(box)

        self.dc_inpt = Slider( "Input", "normal", self, "dc_inpt_lvl" )
        box.append(self.dc_inpt)

        self.dc_tone = Slider( "Tone", "normal", self, "dc_tone_lvl" )
        box.append(self.dc_tone)

        self.dc_outd = Toggle("Out D+/E")
        self.bind_property(
            "dc_outd_sw", self.dc_outd,
            "active", GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )
        box.append(self.dc_outd)

        self.dc_rept = Slider( "Repeat", "repeat", self, "dc_rept_lvl" )
        box.append(self.dc_rept)

        self.dc_ints = Slider( "Intensity", "normal", self, "dc_ints_lvl" )
        box.append(self.dc_ints)

        box = BoxInner("Volume")
        self.append(box)

        self.dc_volm = Slider( "Volume", "normal", self, "dc_volm_lvl" )
        box.append(self.dc_volm)

