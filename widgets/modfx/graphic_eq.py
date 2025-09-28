import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GObject# GLib, Gdk, 

from widgets.slider import Slider
from widgets.box_inner import BoxInner

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from lib.effect import Effect
from lib.set_mapping import add_properties

@add_properties()
class GraphicEq(Effect, Gtk.Box):
    ge_31h_lvl    = GObject.Property(type=int, default=0)
    ge_62h_lvl    = GObject.Property(type=int, default=0)
    ge_125h_lvl     = GObject.Property(type=int, default=0)
    ge_250h_lvl     = GObject.Property(type=int, default=0)
    ge_500h_lvl     = GObject.Property(type=int, default=0)
    ge_1kh_lvl     = GObject.Property(type=int, default=0)
    ge_2kh_lvl     = GObject.Property(type=int, default=0)
    ge_4kh_lvl     = GObject.Property(type=int, default=0)
    ge_8kh_lvl     = GObject.Property(type=int, default=0)
    ge_16kh_lvl     = GObject.Property(type=int, default=0)
    ge_lev_lvl      = GObject.Property(type=int, default=0)

    def __init__(self, ctrl, pprefx=""):
        super().__init__(ctrl, self.mapping, pprefx)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(3)
        self.parent_prefix = pprefx
        
        box_co = BoxInner()

        self.ge_31h = Slider( "31 Hz", "gain", self, "ge_31h_lvl" )
        box_co.append(self.ge_31h)

        self.ge_62h = Slider( "62 Hz", "gain", self, "ge_62h_lvl" )
        box_co.append(self.ge_62h)

        self.ge_125h = Slider( "125 Hz", "gain", self, "ge_125h_lvl" )
        box_co.append(self.ge_125h)

        self.ge_250h = Slider( "250 Hz", "gain", self, "ge_250h_lvl" )
        box_co.append(self.ge_250h)

        self.ge_500h = Slider( "500 Hz", "gain", self, "ge_500h_lvl" )
        box_co.append(self.ge_500h)

        self.ge_1kh = Slider( "1 kHz", "gain", self, "ge_1kh_lvl" )
        box_co.append(self.ge_1kh)

        self.ge_2kh = Slider( "2 kHz", "gain", self, "ge_2kh_lvl" )
        box_co.append(self.ge_2kh)

        self.ge_4kh = Slider( "4 kHz", "gain", self, "ge_4kh_lvl" )
        box_co.append(self.ge_4kh)

        self.ge_8kh = Slider( "8 kHz", "gain", self, "ge_8kh_lvl" )
        box_co.append(self.ge_8kh)

        self.ge_16kh = Slider( "16 kHz", "gain", self, "ge_16kh_lvl" )
        box_co.append(self.ge_16kh)

        box_lvl = BoxInner()
        self.lev = Slider( "Level", "gain", self, "ge_lev_lvl" )
        box_lvl.append(self.lev)

        self.append(box_co)
        self.append(box_lvl)


