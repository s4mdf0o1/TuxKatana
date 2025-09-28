
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
class Phaser(Effect, Gtk.Box):
    ro_rate_lvl     = GObject.Property(type=int, default=0)
    ro_dept_lvl     = GObject.Property(type=int, default=0)
    ro_levl_lvl     = GObject.Property(type=int, default=0)

    def __init__(self, ctrl, pprefx=""):
        super().__init__(ctrl, self.mapping, pprefx)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(6)
        self.parent_prefix = pprefx
    
        box = BoxInner("Rotary")
        self.append(box)

        self.ro_rate = Slider( "Rate", "normal", self, "ro_rate_lvl" )
        box.append(self.ro_rate)

        self.ro_dept = Slider( "Depth", "normal", self, "ro_dept_lvl" )
        box.append(self.ro_dept)

        box = BoxInner("Level")
        self.append(box)

        self.ro_levl = Slider( "Level", "normal", self, "ro_levl_lvl" )
        box.append(self.ro_dmix)

