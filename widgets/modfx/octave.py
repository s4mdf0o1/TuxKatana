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
class Octave(Effect, Gtk.Box):
    oc_type         = GObject.Property(type=str)
    oc_type_idx     = GObject.Property(type=int, default=0)
    oc_eff_lvl      = GObject.Property(type=int, default=0)
    oc_dmix_lvl     = GObject.Property(type=int, default=0)

    def __init__(self, ctrl, pprefx=""):
        super().__init__(ctrl, self.mapping, pprefx)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(6)
        self.parent_prefix = pprefx
    
        box_oc = BoxInner("Octave")
        self.append(box_oc)

        self.types_list = ComboStore( self, self.types, "oc_type_idx")
        box_oc.append(self.types_list)

        box_lv = BoxInner("Level")
        self.append(box_lv)

        self.eff = Slider( "Effect", "normal", self, "oc_eff_lvl" )
        box_lv.append(self.eff)

        self.dmix = Slider( "Direct Mix", "normal", self, "oc_dmix_lvl" )
        box_lv.append(self.dmix)

