from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from lib.midi_bytes import Address, MIDIBytes

from lib.map import Map
from .common import Common
from ruamel.yaml import YAML
yaml = YAML(typ="rt")


class Compressor(Common, GObject.GObject):
    __gsignals__ = {
        "compressor-map-ready": (GObject.SIGNAL_RUN_FIRST, None, (object,)),
    }
    co_type         = GObject.Property(type=int, default=0)
    co_type_idx     = GObject.Property(type=int, default=0)
    co_sus_lvl      = GObject.Property(type=float, default=0.0)
    co_att_lvl      = GObject.Property(type=float, default=0.0)
    co_tone_lvl      = GObject.Property(type=float, default=0.0)
    co_eff_lvl      = GObject.Property(type=float, default=0.0)
    # co_dmix_lvl     = GObject.Property(type=float, default=0.0)

    def __init__(self, device, ctrl):
        super().__init__(device, ctrl, "Compressor")
        # GObject.GObject.__init__()
        # self.name = "Compressor"
        self.ctrl = ctrl
        self.device = device
        # self.map = Map("params/modfx/compressor.yaml")
        # self.prefix = None
        # self.set_mry_map()

        # self.banks=['G', 'R', 'Y']

        # self.mry_id = device.mry.connect("mry-loaded", self.load_from_mry)
        self.notify_id = self.connect("notify", self.set_from_ui)
        self.load_map(device)


    def load_map(self, device):
        # log.debug(f"{self.map}")
        self.emit("compressor-map-ready", self.map['CompressorTypes'])#, self.map['Modes'])

    # def set_from_msg(self, name, value):
    #     name = name.replace('-', '_')
    #     log.debug(f">>> {name} = {value} {self.prefix=}")
    #     self.direct_set(name, value)

    def search_addr(self, prop):
        for k, v in self.device.mry.map.items():
            o, p = v
            if p == prop:
                return k

    def set_from_ui(self, obj, pspec):
        name = pspec.name
        value = self.get_property(name)
        # log.debug(f"{name}={value} {self.prefix=}")
        name = self.prefix + '_' +name.replace('-','_')
        Addr = self.search_addr(name)
        log.debug(f">>> [{Addr}]> {name}={value}")
        if isinstance(value, float):
            value = int(value)
        ## DEBUG Memory MAP Dict
        # mry_map = self.device.mry.map.copy()
        # for k, v in mry_map.items():
        #     obj, prop = v
        #     mry_map[k]= prop
        # with open(self.prefix+"map.log", 'w') as f:
        #     yaml.dump(mry_map, f)

        if 'co_type_idx' in name:
            model_val = list(self.map['CompressorTypes'].values())[value]
            prop = self.prefix+'_'+"co_type"
            Addr = self.search_addr(prop)
            log.debug(f"{prop=} {Addr}")
            if Addr:
                self.ctrl.send(Addr, model_val, True)
        elif 'lvl' in name:
            if Addr:
                self.ctrl.send(Addr, value, True)
        elif not Addr:
            log.warning(f"{name} not found in device.mry.map")

        # else:
        #     self.ctrl.send(Addr, value, True)

    # def direct_set(self, prop, value):
    #     self.handler_block_by_func(self.set_from_ui)
    #     self.handler_block(self.notify_id)
    #     self.set_property(prop, value)
    #     self.handler_unblock(self.notify_id)
    #     self.handler_unblock_by_func(self.set_from_ui)

    # def load_from_mry(self, mry):
    #     for saddr, prop in self.map.recv.items():
    #         value = mry.read(Address(saddr))
    #         log.debug(f"[{saddr}]: {prop}={value}")
    #         self.direct_set(prop, value.int)

    # def set_mry_map(self):
    #     for Addr, prop in self.map.recv.items():
    #         prop = self.prefix + "_" + prop
    #         Addr = Address(Addr)+256 if self.prefix=='fx' else Addr
    #         log.debug(f"[{Addr}]> {prop}")
    #         self.device.mry.map[str(Addr)] = ( self, prop) 


