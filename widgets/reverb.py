import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

from .slider import Slider
from .tabbed_panel import TabbedPanel
from .bank import Bank
from .toggle import Toggle
from .combo_store import ComboStore
from .box_inner import BoxInner
from lib.effect import Effect

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from lib.set_mapping import add_properties

@add_properties()
class Reverb(Effect, Gtk.Box):
    reverb_sw       = GObject.Property(type=bool, default=False)
    re_type         = GObject.Property(type=int, default=0)
    re_type_idx     = GObject.Property(type=int, default=0)
    re_status       = GObject.Property(type=int, default=0)
    re_bank_sel        = GObject.Property(type=int, default=0)
    re_bank_G          = GObject.Property(type=int, default=0)
    re_bank_R          = GObject.Property(type=int, default=0)
    re_bank_Y          = GObject.Property(type=int, default=0)
    re_mode_idx     = GObject.Property(type=int, default=0)
    re_mode         = GObject.Property(type=int, default=0)
    re_mode_G          = GObject.Property(type=int, default=0)
    re_mode_R          = GObject.Property(type=int, default=0)
    re_mode_Y          = GObject.Property(type=int, default=0)
    re_pre_delay_lvl   = GObject.Property(type=int, default=0)
    re_time_lvl        = GObject.Property(type=int, default=0)
    re_density_lvl     = GObject.Property(type=int, default=0)
    re_low_cut_lvl     = GObject.Property(type=int, default=0)
    re_high_cut_lvl    = GObject.Property(type=int, default=0)
    re_effect_lvl      = GObject.Property(type=int, default=0)
    re_dmix_lvl     = GObject.Property(type=int, default=0)
    re_vol_lvl      = GObject.Property(type=int, default=0)

    def __init__(self, ctrl):
        super().__init__(ctrl, self.mapping)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(6)

        # self.stores = {'Types': [], 'Modes': []}
        
        banks = {"GREEN":'1', "RED":'2', "YELLOW":'3'}
        self.bank = Bank("REVERB", banks)
        self.bank.buttons[0].set_status_id(1)
        self.bank.buttons[2].set_status_id(3)
        self.append(self.bank)

        self.bind_property(
            "re_bank_sel", self.bank, "selected",
            GObject.BindingFlags.BIDIRECTIONAL |\
            GObject.BindingFlags.SYNC_CREATE )

        box_sel = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)

        self.types_store = ComboStore( self, self.types, 're_type_idx')
        box_sel.append(self.types_store)

        self.modes_store = ComboStore( self, self.modes, 're_mode_idx')
        box_sel.append(self.modes_store)

        self.volume = Slider( 
                "Volume", "normal", self, "re_vol_lvl" )
        self.volume.set_hexpand(True)
        box_sel.append(self.volume)

        self.append(box_sel)

        box_revb = BoxInner("Reverb")
        self.pre_delay = Slider(
                "Pre Delay", "time_500ms", self, "re_pre_delay_lvl" )
        box_revb.append(self.pre_delay)

        self.time = Slider(
                "Time", "time_10s", self, "re_time_lvl" )
        box_revb.append(self.time)

        self.density = Slider( 
                "Density", "density", self, "re_density_lvl" )
        box_revb.append(self.density)

        self.append(box_revb)

        box_filt = BoxInner("Filter")
        self.low_cut = Slider(
                "Low Cut", "low_freq", self, "re_low_cut_lvl" )
        box_filt.append(self.low_cut)

        self.high_cut= Slider(
                "High Cut", "high_freq", self, "re_high_cut_lvl" )
        box_filt.append(self.high_cut)

        self.append(box_filt)

        box_lvl = BoxInner("Level")
        self.effect= Slider(
                "Effect", "normal", self, "re_effect_lvl" )
        box_lvl.append(self.effect)

        self.dir_mix= Slider(
                "Direct Mix", "normal", self, "re_dmix_lvl" )
        box_lvl.append(self.dir_mix)

        self.append(box_lvl)


