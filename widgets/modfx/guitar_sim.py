import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

from widgets.slider import Slider
from widgets.toggle import Toggle
from widgets.box_inner import BoxInner
from widgets.combo_store import ComboStore

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from lib.effect import Effect
from lib.set_mapping import add_properties

@add_properties()
class GuitarSim(Effect, Gtk.Box):
    gs_type         = GObject.Property(type=str)
    gs_type_idx     = GObject.Property(type=int, default=0)
    gs_low_lvl      = GObject.Property(type=int, default=0)
    gs_high_lvl      = GObject.Property(type=int, default=0)
    gs_eff_lvl      = GObject.Property(type=int, default=0)
    gs_bod_lvl      = GObject.Property(type=int, default=0)

    def __init__(self, ctrl, pprefx=""):
        super().__init__(ctrl, self.mapping, pprefx)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(6)
        self.parent_prefix = pprefx
 
        box_gs = BoxInner("Guitar Sim")
        self.types_list = ComboStore( self, self.types, "gs_type_idx")
        box_gs.append(self.types_list)

        self.low_lvl = Slider( "Low", "plus_minus", self, "gs_low_lvl" )
        box_gs.append(self.low_lvl)

        self.high_lvl = Slider( "High", "plus_minus", self, "gs_high_lvl" )
        box_gs.append(self.high_lvl)

        self.bod_lvl = Slider( "Body", "normal", self, "gs_bod_lvl" )
        box_gs.append(self.bod_lvl)

        self.eff_lvl = Slider( "Effect", "normal", self, "gs_eff_lvl" )
        box_gs.append(self.eff_lvl)

        self.append(box_gs)


