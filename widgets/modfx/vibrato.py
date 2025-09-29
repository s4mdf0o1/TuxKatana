
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
class Vibrato(Effect, Gtk.Box):
    vi_rate_lvl     = GObject.Property(type=int, default=0)
    vi_dept_lvl     = GObject.Property(type=int, default=0)
    vi_levl_lvl     = GObject.Property(type=int, default=0)

    def __init__(self, ctrl, pprefx=""):
        super().__init__(ctrl, self.mapping, pprefx)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(6)
        self.parent_prefix = pprefx

        box = BoxInner("Vibrato")
        self.append(box)

        self.vi_rate = Slider( "Rate", "normal", self, "vi_rate_lvl" )
        box.append(self.vi_rate)

        self.vi_dept = Slider( "Depth", "normal", self, "vi_dept_lvl" )
        box.append(self.vi_dept)

        box = BoxInner("Level")
        self.append(box)

        self.vi_levl = Slider( "Level", "normal", self, "vi_levl_lvl" )
        box.append(self.vi_levl)


