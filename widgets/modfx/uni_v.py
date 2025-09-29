
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
class UniV(Effect, Gtk.Box):
    uv_rate_lvl     = GObject.Property(type=int, default=0)
    uv_dept_lvl     = GObject.Property(type=int, default=0)
    uv_levl_lvl     = GObject.Property(type=int, default=0)

    def __init__(self, ctrl, pprefx=""):
        super().__init__(ctrl, self.mapping, pprefx)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(6)
        self.parent_prefix = pprefx
    
        box = BoxInner("Uni-V")
        self.append(box)

        self.uv_rate = Slider( "Rate", "normal", self, "uv_rate_lvl" )
        box.append(self.uv_rate)

        self.uv_dept = Slider( "Depth", "normal", self, "uv_dept_lvl" )
        box.append(self.uv_dept)

        box = BoxInner("Level")
        self.append(box)

        self.uv_levl = Slider( "Level", "normal", self, "uv_levl_lvl" )
        box.append(self.uv_levl)

