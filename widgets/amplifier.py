import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

from .slider import Slider
from .bank import Bank
from .combo_store import ComboStore
from .box_inner import BoxInner
from lib.effect import Effect
from lib.midi_bytes import Address, MIDIBytes

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from .toggle import Toggle

from lib.set_mapping import add_properties

@add_properties()
class Amplifier(Effect, Gtk.Box):
    am_num         = GObject.Property(type=int, default=-1)        # Amp LEDs
    am_var_sw       = GObject.Property(type=bool, default=False)
    am_type         = GObject.Property(type=str)                    # Real Model Code
    am_type_idx     = GObject.Property(type=int, default=-1)        # Combo index
    am_gain_lvl     = GObject.Property(type=int, default=0)
    am_vol_lvl      = GObject.Property(type=int, default=0)
    am_bass_lvl     = GObject.Property(type=int, default=0)
    am_middle_lvl   = GObject.Property(type=int, default=0)
    am_treble_lvl   = GObject.Property(type=int, default=0)
    am_unk1_lvl     = GObject.Property(type=int, default=0)
    am_unk2_lvl     = GObject.Property(type=int, default=0)

    def __init__(self, ctrl):
        super().__init__(ctrl, self.mapping)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(6)
        # self.ctrl = ctrl
        self.switch_model = False

        bank_buttons = dict(list(self.types.items())[:5])
        self.bank = Bank("TYPE", bank_buttons)
        self.append(self.bank)
        self.bind_property(
            "am_num", self.bank, "selected",
            GObject.BindingFlags.BIDIRECTIONAL |\
            GObject.BindingFlags.SYNC_CREATE )

        self.store = ComboStore( self, self.types, 'am_type_idx')
        self.append(self.store)

        self.tog_var = Toggle("Variation")
        self.tog_var.name = "am_var_sw"
        self.bind_property(
            "am_var_sw", self.tog_var,
            "active", GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )
        self.append(self.tog_var)

        self.sld_gain = Slider( "Gain", "normal", self, "am_gain_lvl" )
        self.append(self.sld_gain)

        self.sld_volume = Slider( "Volume", "normal", self, 'am_vol_lvl' )
        self.append(self.sld_volume)

        box_eq = BoxInner("Equalizer")
        self.bass = Slider( "Bass", "normal", self, 'am_bass_lvl' )
        self.middle = Slider( "Middle", "normal", self, 'am_middle_lvl' )
        self.treble = Slider( "Treble", "normal", self, 'am_treble_lvl' )
        box_eq.append(self.treble)
        box_eq.append(self.middle)
        box_eq.append(self.bass)
        self.append(box_eq)

        box_unk = BoxInner("Unknown")
        self.sld_unk_1 = Slider( "Unknown 1", "normal", self, 'am_unk1_lvl' )
        self.sld_unk_2 = Slider( "Unknown 2", "normal", self, 'am_unk2_lvl' )
        box_unk.append(self.sld_unk_1 )
        box_unk.append(self.sld_unk_2 )
        self.append(box_unk)
        self.mry.connect("mry-loaded", self.set_am_type)
        
    def on_mry_changed(self, mry, addr, val):
        prop = self.mapping.inverse.get(addr, None)
        if not prop:
            return
        # log.debug(f">>> {addr}: {prop}={val}({type(val)})")
        current = self.get_property(prop)
        val_type = self.find_property(prop).value_type.name
        if val_type == 'gboolean':
            val = val.bool
        # log.debug(f"{addr}: {prop}={val}({type(val)}) {current=}({type(current)})")
        if prop == 'am_type':
            svalue = str(val)
            num = list(self.types.values()).index(svalue)
            self.direct_set('am_type_idx', num)
        elif prop == 'am_num':
            self.direct_set(prop, val.int)
        else:
            super().on_mry_changed(mry, addr, val)

    def on_ui_changed(self, obj, pspec):
        name = pspec.name.replace('-', '_')
        value = obj.get_property(pspec.name)
        if not name in self.mapping and not '_idx' in name:
            return
        # value = self.get_property(name)
        # log.debug(f"<<< {name} = {value}")
        # addr = self.mapping.get(name, None)
        if name == 'am_type_idx':
            model_val = list(self.types.inverse)[value]
            addr  = self.mapping.get("am_type", None)
            current = self.mry.get_value(addr)
            # log.debug(f"{name=} {addr=} {model_val=} {current=} {self.mry.get_value(addr)=}")
            if current != model_val:
                self.direct_mry(addr, model_val)
        elif name in ["am_var_sw", "am_num"]:
            num = value if name == 'am_num' else self.am_num
            var = value if name == 'am_var_sw' else self.am_var_sw
            index = num + (5 if var else 0)
            # log.debug(self.types)
            am_type = list(self.types.inverse.keys())[index]
            addr = self.mapping.get("am_type", None)
            am_type = MIDIBytes(am_type)
            current = self.am_type_idx
            self.direct_set("am_type", am_type)
            if not self.switch_model:
                # log.debug(f"{name=} {addr=} {index=} {current=}")
                self.direct_mry(addr, am_type)
                self.direct_set("am_type_idx", index)
        else:
            super().on_ui_changed(obj, pspec)

    def set_am_type(self, mry):
        addr = self.mapping.get("am_type", None)
        val = self.mry.read(addr)
        svalue = str(val)
        num = list(self.types.values()).index(svalue)
        self.direct_set('am_type_idx', num)

    # def on_mry_loaded(self, mry):
    #     log.debug("load mry")
    #     for prop, addr in self.mapping.items():
    #         val = mry.read(addr)
    #         log.debug(f"{addr}: {prop}={val}")
    #         # val = self.type_val(prop, val)
    #         if val != None:
    #             self.direct_set(prop, val)
 
