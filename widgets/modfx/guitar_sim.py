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

class GuitarSimUI(Gtk.Box):
    def __init__(self, own_ctrl):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.own_ctrl = own_ctrl
        
        box_gs = BoxInner("Guitar Sim")
        self.types = ComboStore( own_ctrl, 'Types', True)
        box_gs.append(self.types)

        self.low_lvl = Slider( "Low", "plus_minus", self.own_ctrl, "gs_low_lvl" )
        box_gs.append(self.low_lvl)

        self.high_lvl = Slider( "High", "plus_minus", self.own_ctrl, "gs_high_lvl" )
        box_gs.append(self.high_lvl)

        self.bod_lvl = Slider( "Body", "normal", self.own_ctrl, "gs_bod_lvl" )
        box_gs.append(self.bod_lvl)

        self.eff_lvl = Slider( "Effect", "normal", self.own_ctrl, "gs_eff_lvl" )
        box_gs.append(self.eff_lvl)

        self.append(box_gs)


