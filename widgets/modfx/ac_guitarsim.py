
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
class AcGuitarsim(Effect, Gtk.Box):
    ag_top_lvl      = GObject.Property(type=int, default=0)
    ag_body_lvl     = GObject.Property(type=int, default=0)
    ag_low_lvl      = GObject.Property(type=int, default=0)
    ag_high_lvl     = GObject.Property(type=int, default=0)
    ag_levl_lvl     = GObject.Property(type=int, default=0)

    def __init__(self, ctrl, pprefx=""):
        super().__init__(ctrl, self.mapping, pprefx)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        # self.set_spacing(3)
        self.parent_prefix = pprefx

        box = BoxInner("TODO")
        self.append(box)

        self.ag_top = Slider( "Top", "plus_minus", self, "ag_top_lvl" )
        box.append(self.ag_top)

        self.ag_body = Slider( "Body", "normal", self, "ag_body_lvl" )
        box.append(self.ag_body)

        self.ag_low = Slider( "Low", "plus_minus", self, "ag_low_lvl" )
        box.append(self.ag_low)

        self.ag_high = Slider( "High", "plus_minus", self, "ag_high_lvl" )
        box.append(self.ag_high)

        box = BoxInner("Level")
        self.append(box)

        self.ag_lvl = Slider( "Level", "normal", self, "ag_levl_lvl" )
        box.append(self.ag_levl)


