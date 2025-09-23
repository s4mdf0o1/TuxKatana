from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from .midi_bytes import Address, MIDIBytes

from .map import Map
from .effect import Effect

class Reverb(Effect, GObject.GObject):
    __gsignals__ = {
        "reverb-map-ready": (GObject.SIGNAL_RUN_FIRST, None, (object,)),
    }
    reverb_sw       = GObject.Property(type=bool, default=False)
    re_type     = GObject.Property(type=int, default=0)
    re_type_idx        = GObject.Property(type=int, default=0)
    reverb_status   = GObject.Property(type=int, default=0)
    bank_select     = GObject.Property(type=int, default=0)
    bank_G          = GObject.Property(type=int, default=0)
    bank_R          = GObject.Property(type=int, default=0)
    bank_Y          = GObject.Property(type=int, default=0)
    re_mode_idx        = GObject.Property(type=int, default=0)
    re_mode        = GObject.Property(type=int, default=0)
    mode_G          = GObject.Property(type=int, default=0)
    mode_R          = GObject.Property(type=int, default=0)
    mode_Y          = GObject.Property(type=int, default=0)
    pre_delay_lvl   = GObject.Property(type=float, default=0.0)
    time_lvl        = GObject.Property(type=float, default=0.0)
    density_lvl     = GObject.Property(type=float, default=0.0)
    low_cut_lvl     = GObject.Property(type=float, default=0.0)
    high_cut_lvl    = GObject.Property(type=float, default=0.0)
    effect_lvl      = GObject.Property(type=float, default=0.0)
    dir_mix_lvl     = GObject.Property(type=float, default=0.0)
    revb_vol_lvl    = GObject.Property(type=float, default=0.0)

    def __init__(self, device):
        super().__init__("Reverb", device)
        # self.banks=['G', 'R', 'Y']

        # self.notify_id = self.connect("notify", self.set_from_ui)

    def set_from_msg(self, sig_name, value):
        name = sig_name.replace('-', '_')
        # log.debug(f">>> {name} = {value}")
        if name == 're_type':
            svalue = str(MIDIBytes(value))
            num = list(self.map['Types'].values()).index(svalue)
            self.direct_set("re_type_idx", num)
        else:
            super().set_from_msg(sig_name, value)

    def set_from_ui(self, obj, pspec):
        name = pspec.name
        value = self.get_property(name)
        name = name.replace('-', '_')
        # log.debug(f">>> {name} = {value}")
        if isinstance(value, float):
            value = int(value)
        Addr = self.map.get_addr(name)
        if name == 're_type_idx':
            model_val = list(self.map['Types'].values())[value]
            Addr  = self.map.get_addr("re_type")
            self.ctrl.send(Addr, model_val, True)
        elif name == 're_mode_idx':
            mode_val = list(self.map['Modes'].values())[value]
            bank = self.get_bank_var("mode_")
            Addr  =  self.map.get_addr(bank)
            self.ctrl.send(Addr, mode_val, True)
        elif name == 'pre_delay_lvl':#'lvl' in name or name == 'bank_select':
            # if name == 'pre_delay_lvl':
            value = MIDIBytes(value, 2)
            self.ctrl.send(Addr, value, True)
            # else:
                # self.ctrl.send(Addr, value, True)
        # elif 'sw' in name:
            # value = 1 if value else 0
            # self.ctrl.send(Addr, value, True)
        else:
            super().set_from_ui(obj, pspec)

    def get_bank_var(self, var):
        if self.reverb_status <= 0:
            log.warning(f"{self.reverb_status=}")
            return var + self.banks[0]
        else:
            return var + self.banks[self.reverb_status - 1]
        return var+bank

    # def set_bank_type(self):
    #     bank_name = self.get_bank_var("bank_")
    #     r_type = self.get_property(bank_name)
    #     r_type = str(MIDIBytes(r_type))
    #     num = list(self.map['Types'].values()).index(r_type)
    #     self.direct_set("re_type_idx", num)

    # def set_bank_mode(self):
    #     bank_name = self.get_bank_var("mode_")
    #     mode = self.get_property(bank_name)
    #     mode = str(MIDIBytes(mode))
    #     num = list(self.map['Modes'].values()).index(mode)
    #     self.direct_set("re_mode_idx", num)


