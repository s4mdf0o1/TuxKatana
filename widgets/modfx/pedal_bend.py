
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

from widgets.slider import Slider
from widgets.box_inner import BoxInner

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from lib.effect import Effect
from lib.set_mapping import add_properties

@add_properties()
class PedalBend(Effect, Gtk.Box):
    pb_pitc_lvl     = GObject.Property(type=int, default=0)
    pb_ppos_lvl     = GObject.Property(type=int, default=0)
    pb_effl_lvl     = GObject.Property(type=int, default=0)
    pb_dmix_lvl     = GObject.Property(type=int, default=0)

    def __init__(self, ctrl, pprefx=""):
        super().__init__(ctrl, self.mapping, pprefx)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(6)
        self.parent_prefix = pprefx

        box = BoxInner("Pedal Bend")
        self.append(box)

        self.pb_pitc = Slider( "Pitch", "normal", self, "pb_pitc_lvl" )
        box.append(self.pb_pitc)

        self.pb_ppos = Slider( "Pedal Pos.", "normal", self, "pb_ppos_lvl" )
        box.append(self.pb_ppos)

        box = BoxInner("Level")
        self.append(box)

        self.pb_effl = Slider( "Effect", "normal", self, "pb_effl_lvl" )
        box.append(self.pb_effl)

        self.pb_dmix = Slider( "Direct Mix", "normal", self, "pb_dmix_lvl" )
        box.append(self.pb_dmix)

