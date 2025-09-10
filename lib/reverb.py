from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from .tools import to_str, from_str

from .map import Map
from .anti_flood import AntiFlood

class Reverb(AntiFlood, GObject.GObject):
    __gsignals__ = {
        "reverb-loaded": (GObject.SIGNAL_RUN_FIRST, None, (object,object,)),
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
    pre_delay_lvl   = GObject.Property(type=float, default=50.0)
    time_lvl        = GObject.Property(type=float, default=50.0)
    density_lvl     = GObject.Property(type=float, default=50.0)
    low_cut_lvl     = GObject.Property(type=float, default=50.0)
    high_cut_lvl    = GObject.Property(type=float, default=50.0)
    effect_lvl      = GObject.Property(type=float, default=50.0)
    dir_mix_lvl     = GObject.Property(type=float, default=50.0)

    def __init__(self, device, ctrl):
        super().__init__()
        self.name = "Reverb"
        self.ctrl = ctrl
        self.device = device
        #self.name = "REVERB"
        self.map = Map("params/reverb.yaml")
        self.banks=['G', 'R', 'Y']

        self.notify_id = self.connect("notify", self._on_any_property_changed)
        self.mry_id = device.mry.connect("mry-loaded", self.load_from_mry)
        self.set_mry_map()

    def on_param_changed(self, name, value):
        log.debug(f">>> {name} = {value}")
        name = name.replace('-', '_')
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
            self.device.send(from_str(addr), from_str(model_val))
        elif name == 'reverb_status':
            self.direct_set(name, value)
        elif 'lvl' in name or name == 'bank_select':
            self.device.send(addr, [value])
        elif 'sw' in name:
            value = 1 if value else 0
            self.device.send(addr, [value])

    def direct_set(self, prop, value):
        self.handler_block_by_func(self._on_any_property_changed)
        self.set_property(prop, value)
        self.handler_unblock_by_func(self._on_any_property_changed)

    def set_bank_type(self):
        bank = self.banks[self.reverb_status - 1]
        bank_name = "bank_"+bank
        model = self.get_property(bank_name)
        num = list(self.map['Types'].values()).index(to_str(model))
        self.direct_set("type_idx", num)

    def load_from_mry(self, mry):
        for addr, prop in self.map.recv.items():
            value = mry.read_from_str(addr)
            #log.debug(f"{prop}: {addr}: {to_str(value)}")
            if value and value >= 0:
                self.direct_set(prop, value)
        self.set_bank_type()

    def set_mry_map(self):
        for addr, prop in self.map.recv.items():
            #log.debug(f"{addr}: {prop}")
            self.device.mry.map[addr] = ( self, prop) 


