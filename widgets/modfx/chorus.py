
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
class Chorus(Effect, Gtk.Box):
    ch_x_pred_lvl   = GObject.Property(type=float, default=0.0)
    ch_x_rate_lvl   = GObject.Property(type=int, default=0)
    ch_x_dept_lvl   = GObject.Property(type=int, default=0)

    ch_y_pred_lvl   = GObject.Property(type=float, default=0.0)
    ch_y_rate_lvl   = GObject.Property(type=int, default=0)
    ch_y_dept_lvl   = GObject.Property(type=int, default=0)

    ch_xover_lvl    = GObject.Property(type=int, default=0)
    ch_low_lvl      = GObject.Property(type=int, default=0)
    ch_high_lvl     = GObject.Property(type=int, default=0)

    ch_dmix_lvl     = GObject.Property(type=int, default=0)

    def __init__(self, ctrl, pprefx=""):
        super().__init__(ctrl, self.mapping, pprefx)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(6)
        self.parent_prefix = pprefx

        box = BoxInner("High")
        self.append(box)

        self.ch_x_pred = Slider( "Pre Delay", "time_40ms", self, "ch_x_pred_lvl" )
        box.append(self.ch_x_pred)

        self.ch_x_rate = Slider( "Rate", "normal", self, "ch_x_rate_lvl" )
        box.append(self.ch_x_rate)

        self.ch_x_dept = Slider( "Depth", "normal", self, "ch_x_dept_lvl" )
        box.append(self.ch_x_dept)

        box = BoxInner("Low")
        self.append(box)

        self.ch_y_pred = Slider( "Pre Delay", "time_40ms", self, "ch_y_pred_lvl" )
        box.append(self.ch_y_pred)

        self.ch_y_rate = Slider( "Rate", "normal", self, "ch_y_rate_lvl" )
        box.append(self.ch_y_rate)

        self.ch_y_dept = Slider( "Depth", "normal", self, "ch_y_dept_lvl" )
        box.append(self.ch_y_dept)

        self.ch_xover = Slider( "Xover", "xover_freq", self, "ch_xover_lvl" )
        self.append(self.ch_xover)

        # box = BoxInner()
        # self.append(box)

        self.ch_low = Slider( "Low", "normal", self, "ch_low_lvl" )
        self.append(self.ch_low)

        self.ch_high = Slider( "High", "normal", self, "ch_high_lvl" )
        self.append(self.ch_high)

        self.ch_dmix = Slider( "Direct Mix", "normal", self, "ch_dmix_lvl" )
        self.append(self.ch_dmix)

