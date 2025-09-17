from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from .tools import from_str, to_str
from .address import Address
#import numpy as np

from .map import Map
#from .anti_flood import AntiFlood

class Amplifier(GObject.GObject):
    __gsignals__ = {
        "amp-map-ready": (GObject.SIGNAL_RUN_FIRST, None, (object,)),
    }
    amp_num     = GObject.Property(type=int, default=-1)        # Amp LEDs
    amp_variation = GObject.Property(type=bool, default=False)
    amp_model   = GObject.Property(type=int, default=-1)        # Real Model Code
    model_idx   = GObject.Property(type=int, default=-1)        # Combo index
    gain_lvl    = GObject.Property(type=int, default=50)
    volume_lvl  = GObject.Property(type=int, default=50)

    def __init__(self, device, ctrl):
        super().__init__()
        self.name="Ampli"
        self.ctrl = ctrl
        self.device = device
        self.map = Map("params/amplifier.yaml")
        self.set_mry_map()
        self.switch_model = False

        self.mry_id = device.mry.connect("mry-loaded", self.load_from_mry)
        self.device.connect("load-maps", self.load_map)
        self.notify_id = self.connect("notify", self.set_from_ui)

    def load_map(self, ctrl):
        self.emit("amp-map-ready", self.map['Models'])

    def set_from_msg(self, name, value):
        name = name.replace('-', '_')
        # log.debug(f">>> {name} = {value}")
        if name == 'amp_model':
            svalue = to_str(value)
            num = list(self.map['Models'].values()).index(svalue)
            self.direct_set('model_idx', num)
        else:
            
            self.direct_set(name, value)

    def set_from_ui(self, obj, pspec):
        name = pspec.name
        value = self.get_property(name)
        # log.debug(f">>> {name} = {value}")
        name = name.replace('-', '_')
        if not isinstance(value, (int, bool, float)):
            value = from_str(value)
        if isinstance(value, float):
            value = int(value)
        Addr = self.map.get_addr(name)
        #log.debug(f"{Addr}, {self.map}")
        if name == 'model_idx':
            model_val = list(self.map['Models'].values())[value]
            Addr  = self.map.get_addr("amp_model")
            #Address(self.map.send["amp_model"])
            # log.debug(f"{Addr=} {value}")
            self.device.send(Addr, from_str(model_val))
        elif name in ["amp_variation", "amp_num"]:
            num = value if name == 'amp_num' else self.amp_num
            var = value if name == 'amp_variation' else self.amp_variation
            index = num if not var else num + 5
            amp_model = list(self.map['Models'].values())[index]
            # Addr = Address(self.map.send["amp_model"])
            Addr = self.map.get_addr("amp_model")#send["amp_model"])
            self.direct_set("amp_model", from_str(amp_model)[0])
            if not self.switch_model:
                self.device.send(Addr, from_str(amp_model))
                self.direct_set("model_idx", index)
        elif 'lvl' in name:
            self.device.send(Addr, [value])

    def set_amp_model(self):
        #log.debug(f"{to_str(self.amp_model)=}")
        amp_model = self.device.mry.read(Address("60 00 00 21"))
        self.direct_set("amp_model", amp_model)
        num = list(self.map['Models'].values()).index(to_str(self.amp_model))
        self.direct_set("model_idx", num)
 
    def set_mry_map(self):
        for Addr, prop in self.map.recv.items():
            self.device.mry.map[str(Addr)] = ( self, prop )

    def direct_set(self, prop, value):
        self.handler_block_by_func(self.set_from_ui)
        self.set_property(prop, value)
        self.handler_unblock_by_func(self.set_from_ui)

    def load_from_mry(self, mry):
        #log.debug(self.map.recv.items())
        for saddr, prop in self.map.recv.items():
            value = mry.read(Address(saddr))
            if value is not None and value >= 0:
                self.direct_set(prop, value)
        self.set_amp_model()

