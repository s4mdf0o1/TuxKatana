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
class WaveSynth(Effect, Gtk.Box):
    ws_style_sw    = GObject.Property(type=bool, default=False)
    ws_cuto_lvl    = GObject.Property(type=int, default=0)
    ws_reso_lvl    = GObject.Property(type=int, default=0)
    ws_flts_lvl    = GObject.Property(type=int, default=0)
    ws_fltd_lvl    = GObject.Property(type=int, default=0)
    ws_fltp_lvl    = GObject.Property(type=int, default=0)
    ws_eff_lvl     = GObject.Property(type=int, default=0)
    ws_dmix_lvl    = GObject.Property(type=int, default=0)
    def __init__(self, ctrl, pprefx=""):
        super().__init__(ctrl, self.mapping, pprefx)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(6)
        self.parent_prefix = pprefx
    
        box_ws = BoxInner("Wave Synth")
        self.append(box_ws)

        self.ws_cuto = Slider( "CutOff Freq", "normal", self, "ws_cuto_lvl" )
        box_ws.append(self.ws_cuto)

        self.ws_reso = Slider( "Reson.", "normal", self, "ws_reso_lvl" )
        box_ws.append(self.ws_reso)

        box_ft = BoxInner("Fliter")
        self.append(box_ft)

        self.ws_flts = Slider( "Filter Sens", "normal", self, "ws_flts_lvl" )
        box_ft.append(self.ws_flts)

        self.ws_fltd = Slider( "Filter Decay", "normal", self, "ws_fltd_lvl" )
        box_ft.append(self.ws_fltd)

        self.ws_fltp = Slider( "Filter Depth", "normal", self, "ws_fltp_lvl" )
        box_ft.append(self.ws_fltp)

        box_lv = BoxInner("Level")
        self.append(box_lv)

        self.ws_eff = Slider( "Effect", "normal", self, "ws_eff_lvl" )
        box_lv.append(self.ws_eff)

        self.ws_dmix = Slider( "Direct Mix", "normal", self, "ws_dmix_lvl" )
        box_lv.append(self.ws_dmix)

