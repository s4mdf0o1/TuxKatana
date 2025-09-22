import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

from .slider import Slider
from .bank import Bank
from .combo_store import ComboStore
from .box_inner import BoxInner

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from .toggle import Toggle

class AmplifierUI(Gtk.Box):
    def __init__(self, own_ctrl):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.own_ctrl = own_ctrl

        self.stores = {'Types': []}
        bank_buttons = dict(list(self.own_ctrl.map['Types'].items())[:5])
        self.amp_bank = Bank("TYPE", bank_buttons)
        self.append(self.amp_bank)
        self.own_ctrl.bind_property(
            "amp_num", self.amp_bank, "selected",
            GObject.BindingFlags.BIDIRECTIONAL |\
            GObject.BindingFlags.SYNC_CREATE )

        self.amp_store = ComboStore( own_ctrl, 'Types')
        self.append(self.amp_store)

        self.amp_variation = Toggle("Variation")
        self.amp_variation.name = "amp_variation"
        self.own_ctrl.bind_property(
            "amp_variation", self.amp_variation,
            "active", GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )
        self.append(self.amp_variation)

        self.amp_gain = Slider( "Gain", "normal", self.own_ctrl, "amp_gain_lvl" )
        self.append(self.amp_gain)

        self.amp_volume = Slider( "Volume", "normal", self.own_ctrl, 'amp_vol_lvl' )
        self.append(self.amp_volume)

        box_unk = BoxInner("Unknown")
        self.amp_unk_1 = Slider( "Unknown 1", "normal", self.own_ctrl, 'amp_unk1_lvl' )
        self.amp_unk_2 = Slider( "Unknown 2", "normal", self.own_ctrl, 'amp_unk2_lvl' )
        box_unk.append(self.amp_unk_1 )
        box_unk.append(self.amp_unk_2 )
        self.append(box_unk)

    def on_slider_changed( self, slider, value):
        old_val = self.own_ctrl.get_property(slider.name)
        value = int(value)
        # log.debug(f"{old_val} {value}")
        if value != old_val:
            self.own_ctrl.set_property(slider.name, int(value))

