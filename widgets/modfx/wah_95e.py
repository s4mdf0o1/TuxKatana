
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
class Wah95e(Effect, Gtk.Box):
    w9_ppos_lvl     = GObject.Property(type=int, default=0)
    w9_min_lvl      = GObject.Property(type=int, default=0)
    w9_max_lvl      = GObject.Property(type=int, default=0)
    w9_effc_lvl     = GObject.Property(type=int, default=0)
    w9_dmix_lvl     = GObject.Property(type=int, default=0)

    def __init__(self, ctrl, pprefx=""):
        super().__init__(ctrl, self.mapping, pprefx)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(6)
        self.parent_prefix = pprefx

        box = BoxInner("Wah 95E")
        self.append(box)

        self.w9_ppos = Slider( "Pedal Pos.", "normal", self, "w9_ppos_lvl" )
        box.append(self.w9_ppos)

        box = BoxInner("Settings")
        self.append(box)

        self.w9_min = Slider( "Min", "normal", self, "w9_min_lvl" )
        box.append(self.w9_min)

        self.w9_max = Slider( "Max", "normal", self, "w9_max_lvl" )
        box.append(self.w9_max)

        box = BoxInner("Level")
        self.append(box)

        self.w9_effc = Slider( "Effect", "normal", self, "w9_effc_lvl" )
        box.append(self.w9_effc)

        self.w9_dmix = Slider( "Direct Mix", "normal", self, "w9_dmix_lvl" )
        box.append(self.w9_dmix)


