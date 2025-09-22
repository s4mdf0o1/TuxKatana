import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

from .slider import Slider
from .tabbed_panel import TabbedPanel
from .bank import Bank
from .toggle import Toggle
from .combo_store import ComboStore
from .box_inner import BoxInner

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

class ReverbUI(Gtk.Box):
    def __init__(self, own_ctrl):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.own_ctrl = own_ctrl
        self.stores = {'Types': [], 'Modes': []}
        
        banks = {"GREEN":'1', "RED":'2', "YELLOW":'3'}
        self.bank_select = Bank("REVERB", banks)
        self.bank_select.buttons[0].set_status_id(1)
        self.bank_select.buttons[2].set_status_id(3)
        self.append(self.bank_select)

        self.own_ctrl.bind_property(
            "bank_select", self.bank_select, "selected",
            GObject.BindingFlags.BIDIRECTIONAL |\
            GObject.BindingFlags.SYNC_CREATE )

        box_sel = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)

        self.types = ComboStore( own_ctrl, 'Types')
        box_sel.append(self.types)

        self.modes = ComboStore( own_ctrl, 'Modes')
        box_sel.append(self.modes)

        self.volume_lvl = Slider( 
                "Volume", "normal", own_ctrl, "revb_vol_lvl" )
        self.volume_lvl.set_hexpand(True)
        box_sel.append(self.volume_lvl)

        self.append(box_sel)

        box_revb = BoxInner("Reverb")
        self.pre_delay_lvl = Slider(
                "Pre Delay", "time_500ms", self.own_ctrl, "pre_delay_lvl" )
        box_revb.append(self.pre_delay_lvl)

        self.time_lvl = Slider(
                "Time", "time_10s", self.own_ctrl, "time_lvl" )
        box_revb.append(self.time_lvl)

        self.density_lvl = Slider( 
                "Density", "density", self.own_ctrl, "density_lvl" )
        box_revb.append(self.density_lvl)

        self.append(box_revb)

        box_filt = BoxInner("Filter")
        self.low_cut_lvl = Slider(
                "Low Cut", "low_freq", self.own_ctrl, "low_cut_lvl" )
        box_filt.append(self.low_cut_lvl)

        self.high_cut_lvl = Slider(
                "High Cut", "high_freq", self.own_ctrl, "high_cut_lvl" )
        box_filt.append(self.high_cut_lvl)

        self.append(box_filt)

        box_lvl = BoxInner("Level")
        self.effect_lvl = Slider(
                "Effect", "normal", self.own_ctrl, "effect_lvl" )
        box_lvl.append(self.effect_lvl)

        self.dir_mix_lvl = Slider(
                "Direct Mix", "normal", self.own_ctrl, "dir_mix_lvl" )
        box_lvl.append(self.dir_mix_lvl)

        self.append(box_lvl)


