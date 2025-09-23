import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

from widgets.slider import Slider
from widgets.box_inner import BoxInner

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

class GraphicEqUI(Gtk.Box):
    def __init__(self, own_ctrl):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.own_ctrl = own_ctrl
        
        box_co = BoxInner("Graphic EQ")

        self.ge_31h_lvl = Slider( "31 Hz", "gain", self.own_ctrl, "ge_31h_lvl" )
        box_co.append(self.ge_31h_lvl)

        self.ge_62h_lvl = Slider( "62 Hz", "gain", self.own_ctrl, "ge_62h_lvl" )
        box_co.append(self.ge_62h_lvl)

        self.ge_125h_lvl = Slider( "125 Hz", "gain", self.own_ctrl, "ge_125h_lvl" )
        box_co.append(self.ge_125h_lvl)

        self.ge_250h_lvl = Slider( "250 Hz", "gain", self.own_ctrl, "ge_250h_lvl" )
        box_co.append(self.ge_250h_lvl)

        self.ge_500h_lvl = Slider( "500 Hz", "gain", self.own_ctrl, "ge_500h_lvl" )
        box_co.append(self.ge_500h_lvl)

        self.ge_1kh_lvl = Slider( "1 kHz", "gain", self.own_ctrl, "ge_1kh_lvl" )
        box_co.append(self.ge_1kh_lvl)

        self.ge_2kh_lvl = Slider( "2 kHz", "gain", self.own_ctrl, "ge_2kh_lvl" )
        box_co.append(self.ge_2kh_lvl)

        self.ge_4kh_lvl = Slider( "4 kHz", "gain", self.own_ctrl, "ge_4kh_lvl" )
        box_co.append(self.ge_4kh_lvl)

        self.ge_8kh_lvl = Slider( "8 kHz", "gain", self.own_ctrl, "ge_8kh_lvl" )
        box_co.append(self.ge_8kh_lvl)

        self.ge_16kh_lvl = Slider( "16 kHz", "gain", self.own_ctrl, "ge_16kh_lvl" )
        box_co.append(self.ge_16kh_lvl)

        box_lvl = BoxInner("Level")
        self.lev_lvl = Slider( "Level", "gain", self.own_ctrl, "ge_lev_lvl" )
        box_lvl.append(self.lev_lvl)

        self.append(box_co)
        self.append(box_lvl)


