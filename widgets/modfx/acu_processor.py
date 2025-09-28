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
class AcuProcessor(Effect, Gtk.Box):
    ap_type         = GObject.Property(type=str)
    ap_type_idx     = GObject.Property(type=int, default=0)
    ap_bass_lvl     = GObject.Property(type=int, default=0)
    ap_mid_lvl      = GObject.Property(type=int, default=0)
    ap_mfrq_lvl     = GObject.Property(type=int, default=0)
    ap_treb_lvl     = GObject.Property(type=int, default=0)
    ap_pres_lvl     = GObject.Property(type=int, default=0)
    ap_eff_lvl      = GObject.Property(type=int, default=0)
    # tmp_sw       = GObject.Property(type=bool, default=False)
    def __init__(self, ctrl, pprefx=""):
        super().__init__(ctrl, self.mapping, pprefx)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(6)
        self.parent_prefix = pprefx
    

        self.types_list = ComboStore( self, self.types, 'ap_type_idx')
        self.append(self.types_list)

        box_ft = BoxInner("Freq")
        self.append(box_ft)

        self.ap_bass = Slider( "Bass", "plus_minus", self, "ap_bass_lvl" )
        box_ft.append(self.ap_bass)

        self.ap_mid = Slider( "Middle", "plus_minus", self, "ap_mid_lvl" )
        box_ft.append(self.ap_mid)

        self.ap_mfrq = Slider( "Middle Freq", "mid_freq", self, "ap_mfrq_lvl" )
        box_ft.append(self.ap_mfrq)

        self.ap_treb = Slider( "Treble", "plus_minus", self, "ap_treb_lvl" )
        box_ft.append(self.ap_treb)

        box_lv = BoxInner("Level")
        self.append(box_lv)

        self.ap_pres = Slider( "Presence", "plus_minus", self, "ap_pres_lvl" )
        box_lv.append(self.ap_pres)

        self.ap_eff = Slider( "Effect", "normal", self, "ap_eff_lvl" )
        box_lv.append(self.ap_eff)



