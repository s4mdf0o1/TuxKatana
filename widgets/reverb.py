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
from lib.midi_bytes import MIDIBytes

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from lib.set_mapping import add_properties

@add_properties()
class Reverb(Effect, Gtk.Box):
    reverb_sw       = GObject.Property(type=bool, default=False)
    re_type         = GObject.Property(type=str)
    re_type_idx     = GObject.Property(type=int, default=0)
    re_status       = GObject.Property(type=int, default=0)
    re_bank_sel     = GObject.Property(type=int, default=0)
    re_type_G       = GObject.Property(type=str)
    re_type_R       = GObject.Property(type=str)
    re_type_Y       = GObject.Property(type=str)
    re_mode_idx     = GObject.Property(type=int, default=0)
    re_mode         = GObject.Property(type=str)
    re_mode_G       = GObject.Property(type=str)
    re_mode_R       = GObject.Property(type=str)
    re_mode_Y       = GObject.Property(type=str)
    re_pre_delay_lvl= GObject.Property(type=float, default=0.0)
    re_time_lvl     = GObject.Property(type=int, default=0)
    re_density_lvl  = GObject.Property(type=int, default=0)
    re_low_cut_lvl  = GObject.Property(type=int, default=0)
    re_high_cut_lvl = GObject.Property(type=int, default=0)
    re_effect_lvl   = GObject.Property(type=int, default=0)
    re_dmix_lvl     = GObject.Property(type=int, default=0)
    re_vol_lvl      = GObject.Property(type=int, default=0)

    def __init__(self, ctrl):
        super().__init__(ctrl, self.mapping)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(6)

        banks = {"GREEN":'1', "RED":'2', "YELLOW":'3'}
        self.bank = Bank("REVERB", banks)
        self.bank.buttons[0].set_status_id(1)
        self.bank.buttons[2].set_status_id(3)
        self.append(self.bank)

        self.bind_property(
            "re-bank-sel", self.bank, "selected",
            GObject.BindingFlags.BIDIRECTIONAL |\
            GObject.BindingFlags.SYNC_CREATE )

        box_sel = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)

        self.types_store = ComboStore( self, self.types, 're_type_idx')
        box_sel.append(self.types_store)

        banks = {"REVERB":'02', "DUAL  ⚫": '01', "DELAY 2": '00'}
        self.mode_sel = Bank("", banks)
        self.mode_sel.connect("notify::selected", self.on_mode_changed)
        self.connect("notify::re-mode", self.on_mode_sel)
        self.connect("notify::re-status", self.on_status_changed)

        self.volume = Slider( 
                "Volume", "normal", self, "re_vol_lvl" )
        self.volume.set_hexpand(True)
        box_sel.append(self.volume)

        self.append(box_sel)
        self.append(self.mode_sel)

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

    # def on_ui_changed(self, obj, pspec):
    #     name = pspec.name.replace('-','_')
    #     # log.debug(name)
    #     if not name in self.mapping and not name.endswith('_idx'):
    #         return
    #     super().on_ui_changed(obj, pspec)


    def on_mode_changed(self, bank, pspec):
        selected = bank.get_property(pspec.name.replace('-','_'))
        prop = 're_mode_'+['G','R','Y'][self.re_status-1]
        addr = self.mapping[prop]
        mode = MIDIBytes(bank.buttons[selected].data)

        # log.debug(f"{addr}: {prop} = {mode}")
        self.mry.set_value(addr, mode)

    def on_mode_sel(self, obj, pspec):
        name = pspec.name.replace('-','_')
        sel = obj.get_property(name)
        idx = list(self.modes.inverse).index(sel)
        # log.debug(f"self.mode_sel.buttons[{sel}].set_active(True)")
        self.mode_sel.buttons[idx].set_active(True)

    def on_status_changed(self, obj, pspec):
        val = self.re_status
        # log.debug(f"re_status={val}")
        mode_name = 're_mode_'+['G','R','Y'][val-1]
        bank = 're_type_'+['G','R','Y'][val-1]
        mode_val= self.get_property(mode_name)
        self.set_property('re_mode', mode_val)
        for but in self.mode_sel.buttons:
            if val == 0:
                log.warning("re_status should not be 0")
            else:
                but.set_color(val)

