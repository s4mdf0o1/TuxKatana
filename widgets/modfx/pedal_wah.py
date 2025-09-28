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
class PedalWah(Effect, Gtk.Box):
    pw_type         = GObject.Property(type=str)
    pw_type_idx     = GObject.Property(type=int, default=0)
    pw_pos_lvl      = GObject.Property(type=int, default=0)
    pw_min_lvl      = GObject.Property(type=int, default=0)
    pw_max_lvl      = GObject.Property(type=int, default=0)
    pw_eff_lvl      = GObject.Property(type=int, default=0)
    pw_dmix_lvl      = GObject.Property(type=int, default=0)

    def __init__(self, ctrl, pprefx=""):
        super().__init__(ctrl, self.mapping, pprefx)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(6)
        self.parent_prefix = pprefx
        
        box_pw = BoxInner("Pedal Wah")
        self.types_list = ComboStore( self, self.types, "pw_type_idx")
        box_pw.append(self.types_list)

        self.pos_lvl = Slider( "Pos", "normal", self, "pw_pos_lvl" )
        box_pw.append(self.pos_lvl)

        self.min_lvl = Slider( "Min", "normal", self, "pw_min_lvl" )
        box_pw.append(self.min_lvl)

        self.max_lvl = Slider( "Max", "normal", self, "pw_max_lvl" )
        box_pw.append(self.max_lvl)

        box_lvl = BoxInner("Level")
        self.eff_lvl = Slider( "Effect", "normal", self, "pw_eff_lvl" )
        box_lvl.append(self.eff_lvl)

        self.dmix_lvl = Slider( "Direct Mix", "normal", self, "pw_dmix_lvl" )
        box_lvl.append(self.dmix_lvl)

        self.append(box_pw)
        self.append(box_lvl)


