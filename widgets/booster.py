import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

from .slider import Slider
from .bank import Bank
from .toggle import Toggle
from .box_inner import BoxInner
from .combo_store import ComboStore
from lib.effect import Effect

from lib.midi_bytes import Address, MIDIBytes
from lib.log_setup import LOGGER_NAME
import logging
log = logging.getLogger(LOGGER_NAME)

from lib.set_mapping import add_properties
@add_properties()
class Booster(Effect, Gtk.Box):
    booster_sw   = GObject.Property(type=bool, default=False)
    bo_type      = GObject.Property(type=int, default=0)
    bo_type_idx  = GObject.Property(type=int, default=0)
    bo_solo_sw   = GObject.Property(type=bool, default=False)
    bo_solo_lvl  = GObject.Property(type=int, default=0)
    bo_drive_lvl = GObject.Property(type=int, default=0)
    bo_botm_lvl  = GObject.Property(type=int, default=0)
    bo_tone_lvl  = GObject.Property(type=int, default=0)
    bo_eff_lvl   = GObject.Property(type=int, default=0)
    bo_dmix_lvl  = GObject.Property(type=int, default=0)
    bo_bank_sel  = GObject.Property(type=int, default=0)
    bo_bank_G    = GObject.Property(type=int, default=0)
    bo_bank_R    = GObject.Property(type=int, default=0)
    bo_bank_Y    = GObject.Property(type=int, default=0)
    bo_status    = GObject.Property(type=int, default=0)
    bo_vol_lvl   = GObject.Property(type=int, default=0)

    def __init__(self, ctrl):
        super().__init__(ctrl, self.mapping)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(6)
        # self.stores = {'Types': []}
        
        banks = {"GREEN":'1', "RED":'2', "YELLOW":'3'}
        self.bank_select = Bank("BOOSTER", banks)
        self.bank_select.buttons[0].set_status_id(1)
        self.bank_select.buttons[2].set_status_id(3)
        self.append(self.bank_select)

        self.bind_property(
            "bo_bank_sel", self.bank_select, "selected",
            GObject.BindingFlags.BIDIRECTIONAL |\
            GObject.BindingFlags.SYNC_CREATE )

        box_sel = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        
        # self.bo_store = ComboStore( own_ctrl, 'Types' )
        self.store = ComboStore( self, self.types, 'bo_type_idx')
        box_sel.append(self.store)

        self.volume_lvl = Slider( "Volume", "normal", self, "bo_vol_lvl" )
        box_sel.append(self.volume_lvl)
        self.append(box_sel)

        box_drv = BoxInner("Drive")
        self.drive_lvl = Slider( "Drive", "normal", self, "bo_drive_lvl" )
        adj = self.drive_lvl.scale.get_adjustment()
        adj.set_upper(MIDIBytes('7D').int) # max 100+25
        box_drv.append(self.drive_lvl)

        self.bottom_lvl = Slider( "Bottom", "plus_minus", self, "bo_botm_lvl" )
        box_drv.append(self.bottom_lvl)

        self.tone_lvl = Slider( "Tone", "plus_minus" , self, "bo_tone_lvl" )
        box_drv.append(self.tone_lvl)

        self.append(box_drv)

        box_lvl = BoxInner("Level") 
        self.effect_lvl = Slider( "Effect", "normal", self, "bo_eff_lvl" )
        box_lvl.append(self.effect_lvl)

        self.dmix_lvl = Slider( "Mix", "normal", self, "bo_dmix_lvl" )
        box_lvl.append(self.dmix_lvl)

        self.append(box_lvl)

        box_solo = BoxInner("Solo")
        self.solo_lvl = Slider( "Level", "normal", self, "bo_solo_lvl" )
        box_solo.append(self.solo_lvl)
        self.append(box_solo)

        self.solo_sw = Toggle("SOLO")
        self.bind_property(
            "bo_solo_sw", self.solo_sw, "active", 
            GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )
        box_solo.append(self.solo_sw)

    # def on_ui_changed(self, obj, pspec):
    #     name = pspec.name.replace('-', '_')
    #     value = obj.get_property(pspec.name)
    #     if not name in self.mapping and not '_idx' in name:
    #         return
    #     # value = self.get_property(name)
    #     log.debug(f"<<< {name} = {value}")
    #     # addr = self.mapping.get(name, None)
    #     if name == 'bo_type_idx':
    #         model_val = list(self.types.inverse)[value]
    #         addr  = self.mapping.get("bo_type", None)
    #         current = self.mry.get_value(addr)
    #         # log.debug(f"{name=} {addr=} {model_val=} {current=} {self.mry.get_value(addr)=}")
    #         if current != model_val:
    #             self.direct_mry(addr, model_val)

