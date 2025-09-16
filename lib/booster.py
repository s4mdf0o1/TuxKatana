from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from .tools import to_str, from_str
from .address import Address

from .map import Map
#from .anti_flood import AntiFlood

class Booster(GObject.GObject):
    __gsignals__ = {
        "booster-map-ready": (GObject.SIGNAL_RUN_FIRST, None, (object,)),
    }
    booster_sw      = GObject.Property(type=bool, default=False)
    booster_model   = GObject.Property(type=int, default=0)
    model_idx       = GObject.Property(type=int, default=0)
    solo_sw         = GObject.Property(type=bool, default=False)
    solo_lvl        = GObject.Property(type=float, default=50.0)
    drive_lvl       = GObject.Property(type=float, default=50.0)
    bottom_lvl      = GObject.Property(type=float, default=50.0)
    tone_lvl        = GObject.Property(type=float, default=50.0)
    effect_lvl      = GObject.Property(type=float, default=50.0)
    dir_mix_lvl     = GObject.Property(type=float, default=50.0)
    bank_select     = GObject.Property(type=int, default=0)
    bank_G         = GObject.Property(type=int, default=0)
    bank_R         = GObject.Property(type=int, default=0)
    bank_Y         = GObject.Property(type=int, default=0)
    booster_status  = GObject.Property(type=int, default=0)

    def __init__(self, device, ctrl):
        super().__init__()
        self.name = "Booster"
        self.ctrl = ctrl
        self.device = device
        #self.name = "BOOSTER"
        self.map = Map("params/booster.yaml")
        self.set_mry_map()

        self.banks=['G', 'R', 'Y']

        self.notify_id = self.connect("notify", self.set_from_ui)
        self.mry_id = device.mry.connect("mry-loaded", self.load_from_mry)

        self.device.connect("load-maps", self.load_map)

    def load_map(self, ctrl):
        self.emit("booster-map-ready", self.map['Models'])

    def set_from_msg(self, name, value):
        name = name.replace('-', '_')
        log.debug(f">>> {name} = {value}")
        if name == 'booster_model':
            svalue = to_str(value)
            num = list(self.map['Models'].values()).index(svalue)
            self.direct_set('model_idx', num)
        else:
            self.direct_set(name, value)
        
    def set_from_ui(self, obj, pspec):
        name = pspec.name
        value = self.get_property(name)
        log.debug(f">>> {name} = {value}")
        name = name.replace('-', '_')
        if not isinstance(value, (int, bool, float)):
            value = from_str(value)
        if isinstance(value, float):
            value = int(value)
        Addr = self.map.get_addr(name)
        if name == 'model_idx':
            model_val = list(self.map['Models'].values())[value]
            Addr  = self.map.get_addr("booster_model")#self.map.send["booster_model"]
            self.device.send(Addr, from_str(model_val))
        #elif name == 'booster_status':
        #    self.direct_set(name, value)
        elif 'lvl' in name or name == 'bank_select':
            self.device.send(Addr, [value])
        elif 'sw' in name:
            value = 1 if value else 0
            self.device.send(Addr, [value])

    def direct_set(self, prop, value):
        self.handler_block_by_func(self.set_from_ui)
        self.set_property(prop, value)
        self.handler_unblock_by_func(self.set_from_ui)

    def set_bank_model(self):
        bank = self.banks[self.booster_status - 1]
        bank_name = "bank_"+bank
        model = self.get_property(bank_name)
        num = list(self.map['Models'].values()).index(to_str(model))
        self.direct_set("model_idx", num)

    def load_from_mry(self, mry):
        for saddr, prop in self.map.recv.items():
            value = mry.read(Address(saddr))
            # value = mry.read(Addr)
            #log.debug(f"{prop}: {Addr}: {to_str(value)}")
            if value is not None and value >= 0:
                self.direct_set(prop, value)
        self.set_bank_model()

    def set_mry_map(self):
        for Addr, prop in self.map.recv.items():
            #log.debug(f"{Addr}: {prop}")
            self.device.mry.map[str(Addr)] = ( self, prop) 


