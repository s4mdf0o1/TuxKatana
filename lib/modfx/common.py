from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from lib.midi_bytes import Address, MIDIBytes

from lib.map import Map

class Common:
    def __init__(self, device, ctrl, name):
        super().__init__()
        log.debug(name)
        self.name = name
        self.ctrl = ctrl
        self.device = device
        log.debug(f"params/modfx/{name.lower()}.yaml")
        self.map = Map(f"params/modfx/{name.lower()}.yaml")
        self.prefix = None
        # self.set_mry_map()

        self.banks=['G', 'R', 'Y']

        self.mry_id = device.mry.connect("mry-loaded", self.load_from_mry)
        # self.notify_id = self.connect("notify", self.set_from_ui)
        # self.load_map(device)

    # def load_map(self, device):
        # # log.debug(f"{device}")
        # self.emit("compressor-map-ready", self.map['CompressorTypes'])#, self.map['Modes'])

    def set_from_msg(self, name, value):
        name = name.replace('-', '_')
        log.debug(f">>> {name} = {value} {self.prefix=}")
        self.direct_set(name, value)

    #def set_from_ui(self, obj, pspec):
    #    name = pspec.name
    #    value = self.get_property(name)
    #    name = name.replace(self.prefix+'-', '').replace('-','_')
    #    log.debug(f">>> {name} = {value} {self.prefix=}")
    #    if isinstance(value, float):
    #        value = int(value)
    #    Addr = self.map.get_addr(name)
    #    log.debug(f"{Addr=}")
    #    #if self.effect == 'FX' and Addr and Addr < Address('60 00 06 00'):
    #    #    log.debug(f"FX:{Addr} > {Addr + 256}")
    #    #    Addr += 256
    #    if name == 'co_type_idx':
    #        model_val = list(self.map['CompressorTypes'].values())[value]
    #        Addr  = self.map.get_addr("co_type")
    #        #if self.effect == 'FX' and Addr < Address('60 00 06 00'):
    #        #    Addr += 256
    #        #    log.debug(f"FX:{Addr} > {Addr + 256}")
    #        self.ctrl.send(Addr, model_val, True)
    #    elif 'lvl' in name:
    #        self.ctrl.send(Addr, value, True)
    #    # else:
    #    #     self.ctrl.send(Addr, value, True)

    def direct_set(self, prop, value):
        self.handler_block_by_func(self.set_from_ui)
        # self.handler_block(self.notify_id)
        self.set_property(prop, value)
        # self.handler_unblock(self.notify_id)
        self.handler_unblock_by_func(self.set_from_ui)

    def load_from_mry(self, mry):
        for saddr, prop in self.map.recv.items():
            value = mry.read(Address(saddr))
            log.debug(f"[{saddr}]: {prop}={value}")
            self.direct_set(prop, value.int)

    def set_mry_map(self):
        for Addr, prop in self.map.recv.items():
            prop = self.prefix + "_" + prop
            Addr = Address(Addr)+256 if self.prefix=='fx' else Addr
            log.debug(f"[{str(Addr)}]> {prop}")
            self.device.mry.map[str(Addr)] = ( self, prop) 


