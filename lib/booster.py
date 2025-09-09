from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from .tools import to_str, from_str

from .map import Map
from .anti_flood import AntiFlood

class Booster(AntiFlood, GObject.GObject):
    __gsignals__ = {
        "booster-loaded": (GObject.SIGNAL_RUN_FIRST, None, (object,)),
    }
    booster_sw      = GObject.Property(type=bool, default=False)
    booster_model   = GObject.Property(type=int, default=0)
    model_num             = GObject.Property(type=int, default=0)
    solo_sw         = GObject.Property(type=bool, default=False)
    solo_lvl        = GObject.Property(type=float, default=50.0)
    drive_lvl       = GObject.Property(type=float, default=50.0)
    bottom_lvl      = GObject.Property(type=float, default=50.0)
    tone_lvl        = GObject.Property(type=float, default=50.0)
    effect_lvl      = GObject.Property(type=float, default=50.0)
    dir_mix_lvl     = GObject.Property(type=float, default=50.0)
    bank_select     = GObject.Property(type=int, default=0)
    model_G         = GObject.Property(type=int, default=0)
    #model_G_num     = GObject.Property(type=int, default=0)
    model_R         = GObject.Property(type=int, default=0)
    #model_R_num     = GObject.Property(type=int, default=0)
    model_Y         = GObject.Property(type=int, default=0)
    #model_Y_num     = GObject.Property(type=int, default=0)
    booster_status  = GObject.Property(type=int, default=0)

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
        self.banks=['G', 'R', 'Y']

        self.notify_id = self.connect("notify", self._on_any_property_changed)
        self.mry_id = device.mry.connect("mry-loaded", self.load_from_mry)
        self.addr_id = device.mry.connect("mry-changed", self.addr_changed)
        self.set_mry_map()

    def on_param_changed(self, name, value):
        log.debug(f">>> {name} = {value}")
        name = name.replace('-', '_')
        if not isinstance(value, (int, bool, float)):
            value = from_str(value)
        if isinstance(value, float):
            value = int(value)
        addr = self.map.get_addr(name)
        mry=None
        if addr:
            mry = self.device.mry.read(addr)
        log.debug(f"{to_str(addr)}: {value=}, {mry=}")
        method_name = f"set_{name}"
        method = getattr(self, method_name, None)
        log.debug(f"{method_name} {name}")
        if method and name in ['booster_model', 'model_num', 'booster_status', 'bank_select']:
            method(name, value, addr, mry)
        else:
            log.error(f"{method_name} not found")

    def addr_changed(self, mry, addr):
        if addr in self.map.recv:
            prop = self.map.recv[addr]
            value = mry.read_from_str(addr)
            log.debug(f"{addr=} {prop=} {to_str(value)=}")
    
    def set_booster_model(self, name, value, addr, mry):
        log.debug(f"{name}: {to_str(value)=} / {to_str(addr)=}, {to_str(mry)=}")
        num = list(self.map['Models'].values()).index(to_str(value))
        self.direct_set("model_num", num)

    def set_model_num(self, name, value, addr, mry):
        log.debug(f"{name}: {to_str(value)=}")
        model_val = list(self.map['Models'].values())[value]
        addr  = self.map.send["booster_model"]
        self.device.send(from_str(addr), from_str(model_val))

    def set_booster_status(self, name, value, addr, mry):
        log.debug(f"{name}: {to_str(value)=} / {to_str(addr)=}, {to_str(mry)=}")
        self.direct_set(name, value)

    def set_bank_select(self, name, value, addr, mry):
        log.debug(f"{name}: {to_str(value)=} / {to_str(addr)=}, {to_str(mry)=}")
        self.device.send(addr, [value])

    def set_booster_sw(self, name, value, addr, mry):
        log.debug(f"{name}: {to_str(value)=} / {to_str(addr)=}, {to_str(mry)=}")

    def set_solo_sw(self, name, value, addr, mry):
        log.debug(f"{to_str(addr)}, to_str(value)")

    def set_solo_lvl(self, name, value, addr, mry):
        self.device.send(addr, [value])

    def set_drive_lvl(self, name, value, addr, mry):
        self.device.send(addr, [value])

    def set_bottom_lvl(self, name, value, addr, mry):
        self.device.send(addr, [value])

    def set_tone_lvl(self, name, value, addr, mry):
        self.device.send(addr, [value])

    def set_model_G(self, name, value, addr, mry):
        log.debug(f"{name}: {to_str(value)=} / {to_str(addr)=}, {to_str(mry)=}")

    def set_model_R(self, name, value, addr, mry):
        log.debug(f"{name}: {to_str(value)=} / {to_str(addr)=}, {to_str(mry)=}")

    def set_model_Y(self, name, value, addr, mry):
        log.debug(f"{name}: {to_str(value)=} / {to_str(addr)=}, {to_str(mry)=}")

       #self.handler_block(self.notify_id)
        #self.handler_block_by_func(self._on_any_property_changed)
        #self.bank_status = value
        #self.set_property("name", value)
        #self.handler_unblock_by_func(self._on_any_property_changed)
        #self.handler_unblock(self.notify_id)

  

#    def on_param_changed(self, name, value):
#        log.debug(f">>> {name}={value}")
#        prop_name = name.replace('-', '_')
#        if name == "booster-bank":
#            mry = self.device.mry.read_from_str("60 00 06 39")
#            mry = self.get_mry_from_pname(prop_name)
#            log.debug(f"{mry=}, {value-1=}")
#            #if mry != int(value):
#            addr=from_str(self.map.send[prop_name])
#            self.device.send(addr, [int(value)])
#        if name == "booster-type":
#            idx =list(self.map['Types']['Codes'].values()).index(to_str(value))
#            self.handler_block(self.notify_id)
#            self.set_property("booster_num", idx)
#            self.handler_unblock(self.notify_id)
#        if name == "booster-num":
#            index = self.booster_num
#            code_num = list(self.map['Types']['Codes'].values())[index]
#            addr = from_str(self.map.send["booster_type"])
#            self.device.send(addr, from_str(code_num))
#            #self.handler_block(self.notify_id)
#            #self.set_property("amp_type", index)
#            #self.handler_unblock(self.notify_id)
#        elif name == "booster-driver":
#            addr=from_str(self.map.send[prop_name])
#            mry = mry = self.device.mry.read(addr)
#            if mry != int(value):
#                self.device.send(addr, [int(value)])
            
        


    def get_mry_from_prop(self, prop):
        addr = next((k for k, v in self.map.recv.items() \
                if v == prop), None)
        if addr:
            return self.device.mry.read_from_str(addr)
        return None

    def direct_set(self, prop, value):
        self.handler_block_by_func(self._on_any_property_changed)
        self.set_property(prop, value)
        self.handler_unblock_by_func(self._on_any_property_changed)

    def load_from_mry(self, mry):
        for addr, prop in self.map.send.inverse.items():
            value = mry.read_from_str(addr)
            #log.debug(f"{prop}: {addr}: {to_str(value)}")
            if value:
                self.direct_set(prop, value)

        for addr, prop in self.map.recv.items():
            value = mry.read_from_str(addr)
            #log.debug(f"{prop}: {addr}: {to_str(value)}")
            if value:
                self.direct_set(prop, value)
                #self.handler_block_by_func(self._on_any_property_changed)
                #self.set_property(prop_name, value)
                #self.handler_unblock_by_func(self._on_any_property_changed)
                #self.handler_unblock(self.notify_id)
        #log.debug(f"{self.bank_status=}")
        #log.debug(f"{self.booster_sw=}")

        bank = self.banks[self.booster_status - 1]
        bank_name = "model_"+bank
        model = self.get_property(bank_name)
        num = list(self.map['Models'].values()).index(to_str(model))
        self.direct_set("model_num", num)

    def set_mry_map(self):
        for addr, prop in self.map.recv.items():
            #log.debug(f"{addr}: {prop}")
            self.device.mry.map[addr] = {
                    "obj": self,
                    "prop": prop
                }


