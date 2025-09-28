import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

from widgets.slider import Slider
from widgets.toggle import Toggle
from widgets.box_inner import BoxInner
# from widgets.combo_store import ComboStore

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from lib.effect import Effect
from lib.set_mapping import add_properties

@add_properties()
class SlowGear(Effect, Gtk.Box):
    sg_sens_lvl     = GObject.Property(type=int, default=0)
    sg_rise_lvl     = GObject.Property(type=int, default=0)
    sg_levl_lvl     = GObject.Property(type=int, default=0)
    def __init__(self, ctrl, pprefx=""):
        super().__init__(ctrl, self.mapping, pprefx)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(6)
        self.parent_prefix = pprefx
    
        box_sg = BoxInner("Slow Gear")
        self.append(box_sg)

        self.sens = Slider( "Sens", "normal", self, "sg_sens_lvl" )
        box_sg.append(self.sens)

        self.sens = Slider( "Rise", "normal", self, "sg_rise_lvl" )
        box_sg.append(self.sens)


        box_lvl = BoxInner("Level")
        self.append(box_lvl)

        self.level= Slider( "Sens", "normal", self, "sg_levl_lvl" )
        box_lvl.append(self.level)


