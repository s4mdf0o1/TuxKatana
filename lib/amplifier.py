from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from .tools import from_str, to_str
import numpy as np

from .map import Map
from .anti_flood import AntiFlood

class Amplifier(AntiFlood, GObject.GObject):
    __gsignals__ = {
        "amp-map-ready": (GObject.SIGNAL_RUN_FIRST, None, (object,)),
    }
    amp_num     = GObject.Property(type=int, default=-1)            # Base LEDs
    amp_variation = GObject.Property(type=bool, default=False)
    amp_model   = GObject.Property(type=int, default=-1)            # Real Model Code
    model_idx   = GObject.Property(type=int, default=-1)            # Combo index
    gain_lvl    = GObject.Property(type=int, default=50)
    volume_lvl  = GObject.Property(type=int, default=50)

    def __init__(self, device, ctrl):
        super().__init__()
        self.name="Ampli"
        self.ctrl = ctrl
        self.device = device
        self.map = Map("params/amplifier.yaml")
        self.set_mry_map()


        self.notify_id = self.connect("notify", self._on_any_property_changed)
        self.mry_id = device.mry.connect("mry-loaded", self.load_from_mry)
        self.device.connect("load-maps", self.load_map)

    def load_map(self, ctrl):
        self.emit("amp-map-ready", self.map['Models'])

    def on_param_changed(self, name, value):
        log.debug(f">>> {name} = {value}")
        name = name.replace('-', '_')
        if not isinstance(value, (int, bool, float)):
            value = from_str(value)
        if isinstance(value, float):
            value = int(value)
        addr = self.map.get_addr(name)
        if name == 'amp_model':
            self.set_amp_model()
        elif name == 'model_idx':
            model_val = list(self.map['Models'].values())[value]
            addr  = self.map.send["amp_model"]
            self.device.send(from_str(addr), from_str(model_val))
        elif name in ["amp_variation", "amp_num"]:
            num = value if name == 'amp_num' else self.amp_num
            var = value if name == 'amp_variation' else self.amp_variation
            index = num if not var else num + 5
            amp_model = list(self.map['Models'].values())[index]
            addr = from_str(self.map.send["amp_model"])
            if self.model_idx < 10:
                self.device.send(addr, from_str(amp_model))
        elif 'lvl' in name:
            self.device.send(addr, [value])

    def set_amp_model(self):
        #log.debug(f"{to_str(self.amp_model)=}")
        #if self.amp_model == -1:
        amp_model = self.device.mry.read_from_str("60 00 00 21")
        self.direct_set("amp_model", amp_model)
        num = list(self.map['Models'].values()).index(to_str(self.amp_model))
        #log.debug(f"{num=}")
        self.direct_set("model_idx", num)
 
    def set_mry_map(self):
        for addr, prop in self.map.recv.items():
            self.device.mry.map[addr] = ( self, prop )

    def direct_set(self, prop, value):
        self.handler_block_by_func(self._on_any_property_changed)
        self.set_property(prop, value)
        self.handler_unblock_by_func(self._on_any_property_changed)

    def load_from_mry(self, mry):
        #log.debug(self.map.recv.items())
        for addr, prop in self.map.recv.items():
            value = mry.read_from_str(addr)
            #log.debug(f"{addr}: {prop} = {to_str(value)}")
            #if prop == "amp_model":
            if value is not None and value >= 0:
                self.direct_set(prop, value)
        self.set_amp_model()

