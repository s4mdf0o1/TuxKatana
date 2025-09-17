from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from .tools import to_str, from_str, int_to_midi_bytes
from .address import Address

from .map import Map

class Reverb(GObject.GObject):
    __gsignals__ = {
        "reverb-map-ready": (GObject.SIGNAL_RUN_FIRST, None, (object,object,)),
    }
    reverb_sw       = GObject.Property(type=bool, default=False)
    reverb_type     = GObject.Property(type=int, default=0)
    type_idx        = GObject.Property(type=int, default=0)
    reverb_status   = GObject.Property(type=int, default=0)
    bank_select     = GObject.Property(type=int, default=0)
    bank_G          = GObject.Property(type=int, default=0)
    bank_R          = GObject.Property(type=int, default=0)
    bank_Y          = GObject.Property(type=int, default=0)
    mode_idx        = GObject.Property(type=int, default=0)
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

    def __init__(self, device, ctrl):
        super().__init__()
        self.name = "Reverb"
        self.ctrl = ctrl
        self.device = device
        self.map = Map("params/reverb.yaml")
        self.set_mry_map()

        self.banks=['G', 'R', 'Y']

        self.notify_id = self.connect("notify", self.set_from_ui)
        self.mry_id = device.mry.connect("mry-loaded", self.load_from_mry)

        self.device.connect("load-maps", self.load_map)

    def load_map(self, ctrl):
        self.emit("reverb-map-ready", self.map['Types'], self.map['Modes'])

    def set_from_msg(self, name, value):
        name = name.replace('-', '_')
        # log.debug(f">>> {name} = {value}")
        svalue = to_str(value)
        if name == 'reverb_type':
            num = list(self.map['Types'].values()).index(svalue)
            self.direct_set("type_idx", num)
        else:
            self.direct_set(name, value)

    def set_from_ui(self, obj, pspec):
        name = pspec.name
        value = self.get_property(name)
        name = name.replace('-', '_')
        # log.debug(f">>> {name} = {value}")
        if not isinstance(value, (int, bool, float)):
            value = from_str(value)
        if isinstance(value, float):
            value = int(value)
        Addr = self.map.get_addr(name)
        if name == 'type_idx':
            model_val = list(self.map['Types'].values())[value]
            Addr  = self.map.get_addr("reverb_type")
            self.device.send(Addr, from_str(model_val))
        elif name == 'mode_idx':
            mode_val = list(self.map['Modes'].values())[value]
            bank = self.get_bank_var("mode_")
            Addr  =  self.map.get_addr(bank)
            self.device.send(Addr, from_str(mode_val))
        elif 'lvl' in name or name == 'bank_select':
            if name == 'pre_delay_lvl':
                value = int_to_midi_bytes(value, 2)
                self.device.send(Addr, value)
            else:
                self.device.send(Addr, [value])
        elif 'sw' in name:
            value = 1 if value else 0
            self.device.send(Addr, [value])

    def direct_set(self, prop, value):
        self.handler_block_by_func(self.set_from_ui)
        self.set_property(prop, value)
        self.handler_unblock_by_func(self.set_from_ui)

    def get_bank_var(self, var):
        if self.reverb_status <= 0:
            log.warning(f"{self.reverb_status=}")
            return var + self.banks[0]
        else:
            return var + self.banks[self.reverb_status - 1]
        return var+bank

    def set_bank_type(self):
        bank_name = self.get_bank_var("bank_")
        r_type = self.get_property(bank_name)
        num = list(self.map['Types'].values()).index(to_str(r_type))
        self.direct_set("type_idx", num)

    def set_bank_mode(self):
        bank_name = self.get_bank_var("mode_")
        mode = self.get_property(bank_name)
        num = list(self.map['Modes'].values()).index(to_str(mode))
        self.direct_set("mode_idx", num)


    def load_from_mry(self, mry):
        for saddr, prop in self.map.recv.items():
            value = mry.read(Address(saddr))
            if prop == 'pre_delay_lvl':
                value = mry.read(Address(saddr), 2)
                self.direct_set(prop, value)
            else:
                if value is not None and value >= 0:
                    self.direct_set(prop, value)
        self.set_bank_type()
        self.set_bank_mode()

    def set_mry_map(self):
        for Addr, prop in self.map.recv.items():
            self.device.mry.map[str(Addr)] = ( self, prop) 


