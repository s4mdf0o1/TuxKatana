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
class Compressor(Effect, Gtk.Box):
    co_type         = GObject.Property(type=str)
    co_type_idx     = GObject.Property(type=int, default=0)
    co_sus_lvl      = GObject.Property(type=int, default=0)
    co_att_lvl      = GObject.Property(type=int, default=0)
    co_tone_lvl     = GObject.Property(type=int, default=0)
    co_eff_lvl      = GObject.Property(type=int, default=0)

    def __init__(self, ctrl, pprefx=""):
        super().__init__(ctrl, self.mapping, pprefx)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(6)
        self.parent_prefix = pprefx
        
        box_co = BoxInner("Compressor")
        self.types_list = ComboStore( self, self.types, 'co_type_idx')
        box_co.append(self.types_list)

        self.sus_lvl = Slider( "Sustain", "normal", self, "co_sus_lvl" )
        box_co.append(self.sus_lvl)

        self.att_lvl = Slider( "Attack", "normal", self, "co_att_lvl" )
        box_co.append(self.att_lvl)

        self.tone_lvl = Slider( "Tone", "normal", self, "co_tone_lvl" )
        box_co.append(self.tone_lvl)

        box_lvl = BoxInner("Level")
        self.eff_lvl = Slider( "Effect", "normal", self, "co_eff_lvl" )
        box_lvl.append(self.eff_lvl)

        self.append(box_co)
        self.append(box_lvl)


