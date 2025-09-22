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

class PedalWahUI(Gtk.Box):
    def __init__(self, own_ctrl):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.own_ctrl = own_ctrl
        
        box_pw = BoxInner("Pedal Wah")
        self.types = ComboStore( own_ctrl, 'Types', True)

        box_pw.append(self.types)

        self.pos_lvl = Slider( "Pos", "normal", self.own_ctrl, "pw_pos_lvl" )
        box_pw.append(self.pos_lvl)

        self.min_lvl = Slider( "Min", "normal", self.own_ctrl, "pw_min_lvl" )
        box_pw.append(self.min_lvl)

        self.max_lvl = Slider( "Max", "normal", self.own_ctrl, "pw_max_lvl" )
        box_pw.append(self.max_lvl)

        box_lvl = BoxInner("Level")
        self.eff_lvl = Slider( "Effect", "normal", self.own_ctrl, "pw_eff_lvl" )
        box_lvl.append(self.eff_lvl)

        self.dmix_lvl = Slider( "Direct Mix", "normal", self.own_ctrl, "pw_dmix_lvl" )
        box_lvl.append(self.dmix_lvl)

        self.append(box_pw)
        self.append(box_lvl)


