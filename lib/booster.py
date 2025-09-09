from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from .tools import *

from .map import Map
from .anti_flood import AntiFlood

class Booster(AntiFlood, GObject.GObject):
    __gsignals__ = {
        "booster-loaded": (GObject.SIGNAL_RUN_FIRST, None, (object,)),
    }
    booster_sw      = GObject.Property(type=bool, default=False)
    booster_model   = GObject.Property(type=int, default=0)
    solo_sw         = GObject.Property(type=bool, default=False)
    solo_lvl        = GObject.Property(type=float, default=50.0)
    drive_lvl       = GObject.Property(type=float, default=50.0)
    bottom_lvl      = GObject.Property(type=float, default=50.0)
    tone_lvl        = GObject.Property(type=float, default=50.0)
    effect_lvl      = GObject.Property(type=float, default=50.0)
    dir_mix_lvl     = GObject.Property(type=float, default=50.0)
    bank_select     = GObject.Property(type=int, default=0)
    model_G         = GObject.Property(type=int, default=0)
    model_R         = GObject.Property(type=int, default=0)
    model_Y         = GObject.Property(type=int, default=0)
    bank_status     = GObject.Property(type=int, default=0)

#    booster_bank = GObject.Property(type=int, default=0)
#    booster_status = GObject.Property(type=int, default=0)
#    booster_type = GObject.Property(type=int, default=0)
#    booster_num  = GObject.Property(type=int, default=-1)
#    booster_code = GObject.Property(type=int, default=-1)
#    booster_switch = GObject.Property(type=bool, default=False)
#    booster_driver = GObject.Property(type=float, default=50.0)
    def __init__(self, device, ctrl):
        super().__init__()
        self.ctrl = ctrl
        self.device = device
        self.name = "BOOSTER"
        self.map = Map("params/booster.yaml")

        self.notify_id = self.connect("notify", self._on_any_property_changed)
        self.mry_id = device.mry.connect("mry-changed", self.load_from_mry)
        self.set_mry_map()

    def on_param_changed(self, name, value):
        log.debug(f">>> {name}={value}")
        prop_name = name.replace('-', '_')
        if name == "booster-bank":
            mry = self.device.mry.read_from_str("60 00 06 39")
            mry = self.get_mry_from_pname(prop_name)
            log.debug(f"{mry=}, {value-1=}")
            #if mry != int(value):
            addr=from_str(self.map.send[prop_name])
            self.device.send(addr, [int(value)])
        if name == "booster-type":
            idx =list(self.map['Types']['Codes'].values()).index(to_str(value))
            self.handler_block(self.notify_id)
            self.set_property("booster_num", idx)
            self.handler_unblock(self.notify_id)
        if name == "booster-num":
            index = self.booster_num
            code_num = list(self.map['Types']['Codes'].values())[index]
            addr = from_str(self.map.send["booster_type"])
            self.device.send(addr, from_str(code_num))
            #self.handler_block(self.notify_id)
            #self.set_property("amp_type", index)
            #self.handler_unblock(self.notify_id)
        elif name == "booster-driver":
            addr=from_str(self.map.send[prop_name])
            mry = mry = self.device.mry.read(addr)
            if mry != int(value):
                self.device.send(addr, [int(value)])
            
        


    def get_mry_from_prop(self, prop):
        addr = next((k for k, v in self.map.recv.items() \
                if v == prop), None)
        if addr:
            return self.device.mry.read_from_str(addr)
        return None


    def load_from_mry(self, mry):
        for addr, prop_name in self.map.recv.items():
            value = self.device.mry.read_from_str(addr)
            log.debug(f"{prop_name}: {addr}: {to_str(value)}")
            if value:
                self.set_property(prop_name, value)


    def set_mry_map(self):
        for addr, prop in self.map.recv.items():
            #log.debug(f"{addr}: {prop}")
            self.device.mry.map[addr] = {
                    "obj": self,
                    "prop": prop
                }


