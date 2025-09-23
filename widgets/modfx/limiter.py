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

class LimiterUI(Gtk.Box):
    def __init__(self, own_ctrl):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.own_ctrl = own_ctrl
        
        box_co = BoxInner("Limiter")
        self.types = ComboStore( own_ctrl, 'Types', True)
        box_co.append(self.types)

        self.attak_lvl = Slider( "Attack", "normal", self.own_ctrl, "li_attak_lvl" )
        box_co.append(self.attak_lvl)

        self.thold_lvl = Slider( "Threshold", "normal", self.own_ctrl, "li_thold_lvl" )
        box_co.append(self.thold_lvl)

        self.rate_lvl = Slider( "Rate", "normal", self.own_ctrl, "li_rate_lvl" )
        box_co.append(self.rate_lvl)

        box_lvl = BoxInner("Level")
        self.eff_lvl = Slider( "Effect", "normal", self.own_ctrl, "li_eff_lvl" )
        box_lvl.append(self.eff_lvl)

        self.append(box_co)
        self.append(box_lvl)


