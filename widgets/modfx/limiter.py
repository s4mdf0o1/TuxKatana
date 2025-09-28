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
class Limiter(Effect, Gtk.Box):
    li_type         = GObject.Property(type=str)
    li_type_idx     = GObject.Property(type=int, default=0)
    li_attak_lvl    = GObject.Property(type=int, default=0)
    li_thold_lvl    = GObject.Property(type=int, default=0)
    li_rate_lvl     = GObject.Property(type=int, default=0)
    li_rels_lvl     = GObject.Property(type=int, default=0)
    li_eff_lvl      = GObject.Property(type=int, default=0)
    # li_dmix_lvl     = GObject.Property(type=int, default=0)

    def __init__(self, ctrl, pprefx=""):
        super().__init__(ctrl, self.mapping, pprefx)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(6)
        self.parent_prefix = pprefx
        
        box_co = BoxInner("Limiter")
        self.types_list = ComboStore( self, self.types, "li_type_idx")
        box_co.append(self.types_list)

        self.attak = Slider( "Attack", "normal", self, "li_attak_lvl" )
        box_co.append(self.attak)

        self.thold = Slider( "Threshold", "normal", self, "li_thold_lvl" )
        box_co.append(self.thold)

        self.rate = Slider( "Rate", "normal", self, "li_rate_lvl" )
        box_co.append(self.rate)

        box_lvl = BoxInner("Level")
        self.eff = Slider( "Effect", "normal", self, "li_eff_lvl" )
        box_lvl.append(self.eff)

        self.append(box_co)
        self.append(box_lvl)


