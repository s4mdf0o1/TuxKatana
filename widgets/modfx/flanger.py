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
class Flanger(Effect, Gtk.Box):
    fl_rate_lvl     = GObject.Property(type=int, default=0)
    fl_dept_lvl     = GObject.Property(type=int, default=0)
    fl_man_lvl      = GObject.Property(type=int, default=0)
    fl_reso_lvl     = GObject.Property(type=int, default=0)
    fl_lowc_lvl     = GObject.Property(type=int, default=0)
    fl_eff_lvl      = GObject.Property(type=int, default=0)
    fl_dmix_lvl     = GObject.Property(type=int, default=0)
    def __init__(self, ctrl, pprefx=""):
        super().__init__(ctrl, self.mapping, pprefx)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(6)
        self.parent_prefix = pprefx
    
        box_se = BoxInner("Flanger")
        self.append(box_se)

        self.fl_rate = Slider( "Rate", "normal", self, "fl_rate_lvl" )
        box_se.append(self.fl_rate)

        self.fl_dept = Slider( "Depth", "normal", self, "fl_dept_lvl" )
        box_se.append(self.fl_dept)

        self.fl_man = Slider( "Manual", "normal", self, "fl_man_lvl" )
        box_se.append(self.fl_man)

        self.fl_reso = Slider( "Reson.", "normal", self, "fl_reso_lvl" )
        box_se.append(self.fl_reso)

        self.fl_lowc = Slider( "Low Cut", "low_freq", self, "fl_lowc_lvl" )
        box_se.append(self.fl_lowc)

        box = BoxInner("Level")
        self.append(box)

        self.fl_eff = Slider( "Effect", "normal", self, "fl_eff_lvl" )
        box.append(self.fl_eff)

        self.fl_dmix = Slider( "Direct Mix", "normal", self, "fl_dmix_lvl" )
        box.append(self.fl_dmix)

