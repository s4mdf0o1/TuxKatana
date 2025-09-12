from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from .tools import to_str, from_str, int_to_midi_bytes

from .map import Map
from .anti_flood import AntiFlood

class Reverb(AntiFlood, GObject.GObject):
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
        #self.name = "REVERB"
        self.map = Map("params/reverb.yaml")
        self.set_mry_map()

        self.banks=['G', 'R', 'Y']

        self.notify_id = self.connect("notify", self._on_any_property_changed)
        self.mry_id = device.mry.connect("mry-loaded", self.load_from_mry)

        self.device.connect("load-maps", self.load_map)

    def load_map(self, ctrl):
        self.emit("reverb-map-ready", self.map['Types'], self.map['Modes'])

    def on_param_changed(self, name, value):
        name = name.replace('-', '_')
        #log.debug(f">>> {name} = {value}")
        if not isinstance(value, (int, bool, float)):
            value = from_str(value)
        if isinstance(value, float):
            value = int(value)
        addr = self.map.get_addr(name)
        if name == 'reverb_type':
            num = list(self.map['Types'].values()).index(to_str(value))
            self.direct_set("type_idx", num)
        elif name == 'type_idx':
            model_val = list(self.map['Types'].values())[value]
            addr  = self.map.send["reverb_type"]
            #log.debug(f"name: {addr} {model_val}")
            self.device.send(from_str(addr), from_str(model_val))
        elif 'mode' in name and name.split('_')[1] in self.banks:
            num = list(self.map['Modes'].values()).index(to_str(value))
            self.direct_set("mode_idx", num)
        elif name == 'mode_idx':
            mode_val = list(self.map['Modes'].values())[value]
            bank = self.get_bank_var("mode_")
            addr  = self.map.send[bank]
            #log.debug(f"{name}: {addr} -> {val}")
            self.device.send(from_str(addr), from_str(mode_val))
        elif name == 'reverb_status':
            self.direct_set(name, value)
        elif 'lvl' in name or name == 'bank_select':
            if name == 'pre_delay_lvl':
                value = int_to_midi_bytes(value, 2)
                #log.debug(f"SEND: {name}: {to_str(value)}")
                self.device.send(addr, value)
            else:
                #log.debug(f"SEND: {name}: {to_str(value)}")
                self.device.send(addr, [value])
        elif 'sw' in name:
            value = 1 if value else 0
            #log.debug(f"{name} {to_str(addr)} {to_str(value)}")
            self.device.send(addr, [value])

    def direct_set(self, prop, value):
        self.handler_block_by_func(self._on_any_property_changed)
        self.set_property(prop, value)
        self.handler_unblock_by_func(self._on_any_property_changed)

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
        for addr, prop in self.map.recv.items():
            value = mry.read_from_str(addr)
            if prop == 'pre_delay_lvl':
                #log.debug(prop)
                value = mry.read_from_str(addr, 2)
                self.direct_set(prop, value)
            else:
                if value is not None and value >= 0:
                    self.direct_set(prop, value)
        self.set_bank_type()
        self.set_bank_mode()

    def set_mry_map(self):
        for addr, prop in self.map.recv.items():
            self.device.mry.map[addr] = ( self, prop) 


