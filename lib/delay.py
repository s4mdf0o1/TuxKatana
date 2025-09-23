from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from .midi_bytes import Address, MIDIBytes

from .map import Map
from .effect import Effect

class Delay(Effect, GObject.GObject):
    __gsignals__ = {
        "delay-map-ready": (GObject.SIGNAL_RUN_FIRST, None, (object,)),
    }
    delay_sw        = GObject.Property(type=bool, default=False)
    de_type      = GObject.Property(type=int, default=0)
    de_type_idx        = GObject.Property(type=int, default=0)
    delay_status    = GObject.Property(type=int, default=0)
    bank_select     = GObject.Property(type=int, default=0)
    bank_G          = GObject.Property(type=int, default=0)
    bank_R          = GObject.Property(type=int, default=0)
    bank_Y          = GObject.Property(type=int, default=0)
    time_lvl        = GObject.Property(type=float, default=0.0)
    feedback_lvl    = GObject.Property(type=float, default=0.0)
    tap_time_lvl    = GObject.Property(type=float, default=0.0)
    high_cut_lvl    = GObject.Property(type=float, default=0.0)
    effect_lvl      = GObject.Property(type=float, default=0.0)
    dirmix_lvl      = GObject.Property(type=float, default=0.0)
    d1_time_lvl     = GObject.Property(type=float, default=0.0)
    d1_fb_lvl       = GObject.Property(type=float, default=0.0)
    d1_h_cut_lvl    = GObject.Property(type=float, default=0.0)
    d1_eff_lvl      = GObject.Property(type=float, default=0.0)
    d2_time_lvl     = GObject.Property(type=float, default=0.0)
    d2_fb_lvl       = GObject.Property(type=float, default=0.0)
    d2_h_cut_lvl    = GObject.Property(type=float, default=0.0)
    d2_eff_lvl      = GObject.Property(type=float, default=0.0)
    mod_rate_lvl    = GObject.Property(type=float, default=0.0)
    mod_depth_lvl   = GObject.Property(type=float, default=0.0)
    sde_vint_lpf_sw = GObject.Property(type=bool, default=False)
    sde_fb_phase_sw = GObject.Property(type=bool, default=False)
    sde_ef_phase_sw = GObject.Property(type=bool, default=False)
    sde_filter_sw   = GObject.Property(type=bool, default=False)
    sde_modul_sw    = GObject.Property(type=bool, default=False)
    delay_vol_lvl   = GObject.Property(type=float, default=0.0)

    def __init__(self, device):
        super().__init__("Delay", device  )
        # self.banks=['G', 'R', 'Y']

        self.notify_id = self.connect("notify", self.set_from_ui)

    def set_from_msg(self, name, value):
        name = name.replace('-', '_')
        # log.debug(f">>> {name} = {value}")
        if name == 'de_type':
            svalue = str(MIDIBytes(value))
            num = list(self.map['Types'].values()).index(svalue)
            self.direct_set("de_type_idx", num)
        else:
            self.direct_set(name, value)
 
    def set_from_ui(self, obj, pspec):
        name = pspec.name
        value = self.get_property(name)
        name = name.replace('-', '_')
        # log.debug(f"<<< {name} = {value}")
        if isinstance(value, float):
            value = int(value)
        Addr = self.map.get_addr(name)
        if 'sw' in name:
            value = 1 if value else 0
            self.ctrl.send(Addr, value, True)
        elif name == 'de_type_idx':
            model_val = list(self.map['Types'].values())[value]
            Addr  = self.map.get_addr("de_type")
            self.ctrl.send(Addr, model_val, True)
        elif 'lvl' in name or name == 'bank_select':
            self.ctrl.send(Addr, value, True)
        else:
            log.warning(f"missing DEF for '{name}'")

    def get_bank_var(self, var):
        if self.delay_status == 0:
            log.warning(f"{self.delay_status=}")
            return var + self.banks[0]
        else:
            return var + self.banks[self.delay_status - 1]

    def set_bank_type(self):
        bank_name = self.get_bank_var("bank_")
        d_type = self.get_property(bank_name)
        d_type = str(MIDIBytes(d_type))
        num = list(self.map['Types'].values()).index(d_type)
        self.direct_set("de_type_idx", num)


