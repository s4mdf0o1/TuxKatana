import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

from widgets.slider import Slider
# from .tabbed_panel import TabbedPanel
# from .bank import Bank
from widgets.toggle import Toggle
from widgets.box_inner import BoxInner
from widgets.combo_store import ComboStore

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

class CompressorUI(Gtk.Box):
    def __init__(self, own_ctrl):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.own_ctrl = own_ctrl
        
        box_co = BoxInner("Compressor")
        self.types = ComboStore( own_ctrl, 'Types', True)
        box_co.append(self.types)

        self.sus_lvl = Slider( "Sustain", "normal", self.own_ctrl, "co_sus_lvl" )
        box_co.append(self.sus_lvl)

        self.att_lvl = Slider( "Attack", "normal", self.own_ctrl, "co_att_lvl" )
        box_co.append(self.att_lvl)

        self.tone_lvl = Slider( "Tone", "normal", self.own_ctrl, "co_tone_lvl" )
        box_co.append(self.tone_lvl)

        box_lvl = BoxInner("Level")
        self.eff_lvl = Slider( "Effect", "normal", self.own_ctrl, "co_eff_lvl" )
        box_lvl.append(self.eff_lvl)

        self.append(box_co)
        self.append(box_lvl)


