import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

from .slider import Slider
from .bank import Bank
from .toggle import Toggle
from .box_inner import BoxInner
from .combo_store import ComboStore

from lib.midi_bytes import Address, MIDIBytes
from lib.log_setup import LOGGER_NAME
import logging
log = logging.getLogger(LOGGER_NAME)

class BoosterUI(Gtk.Box):
    def __init__(self, own_ctrl):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.own_ctrl = own_ctrl
        self.stores = {'Types': []}
        
        banks = {"GREEN":'1', "RED":'2', "YELLOW":'3'}
        self.bank_select = Bank("BOOSTER", banks)
        self.bank_select.buttons[0].set_status_id(1)
        self.bank_select.buttons[2].set_status_id(3)
        self.append(self.bank_select)

        self.own_ctrl.bind_property(
            "boost_bank_sel", self.bank_select, "selected",
            GObject.BindingFlags.BIDIRECTIONAL |\
            GObject.BindingFlags.SYNC_CREATE )

        box_sel = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        
        self.boost_store = ComboStore( own_ctrl, 'Types' )
        box_sel.append(self.boost_store)

        self.volume_lvl = Slider( "Volume", "normal", own_ctrl, "boost_vol_lvl" )
        box_sel.append(self.volume_lvl)
        self.append(box_sel)

        box_drv = BoxInner("Drive")
        self.drive_lvl = Slider( "Drive", "normal", self.own_ctrl, "boost_drive_lvl" )
        adj = self.drive_lvl.scale.get_adjustment()
        adj.set_upper(MIDIBytes('7D').int) # max 100+25
        box_drv.append(self.drive_lvl)

        self.bottom_lvl = Slider( "Bottom", "plus_minus", self.own_ctrl, "boost_botm_lvl" )
        box_drv.append(self.bottom_lvl)

        self.tone_lvl = Slider( "Tone", "plus_minus" , self.own_ctrl, "boost_tone_lvl" )
        box_drv.append(self.tone_lvl)

        self.append(box_drv)

        box_lvl = BoxInner("Level") 
        self.effect_lvl = Slider( "Effect", "normal", self.own_ctrl, "boost_eff_lvl" )
        box_lvl.append(self.effect_lvl)

        self.dmix_lvl = Slider( "Mix", "normal", self.own_ctrl, "boost_dmix_lvl" )
        box_lvl.append(self.dmix_lvl)

        self.append(box_lvl)

        box_solo = BoxInner("Solo")
        self.solo_lvl = Slider( "Level", "normal", self.own_ctrl, "boost_solo_lvl" )
        box_solo.append(self.solo_lvl)
        self.append(box_solo)

        self.solo_sw = Toggle("SOLO")
        self.own_ctrl.bind_property(
            "boost_solo_sw", self.solo_sw, "active", 
            GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )
        box_solo.append(self.solo_sw)


