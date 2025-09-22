from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from lib.midi_bytes import Address, MIDIBytes

from lib.map import Map

class Common:
    def __init__(self, device, ctrl, name):
        super().__init__()
        # log.debug(name)
        self.name = name
        self.ctrl = ctrl
        self.device = device
        # log.debug(f"params/modfx/{name.lower()}.yaml")
        self.map = Map(f"params/modfx/{name.lower()}.yaml")
        self.prefix = None
        # self.set_mry_map()

        self.banks=['G', 'R', 'Y']

        self.mry_id = device.mry.connect("mry-loaded", self.load_from_mry)
        # self.notify_id = self.connect("notify", self.set_from_ui)
        # self.load_map(device)

    def set_from_msg(self, name, value):
        name = name.replace('-', '_')
        # log.debug(f">>> {name} = {value} {self.prefix=}")
        self.direct_set(name, value)

    def direct_set(self, prop, value):
        self.handler_block_by_func(self.set_from_ui)
        self.set_property(prop, value)
        self.handler_unblock_by_func(self.set_from_ui)

    def load_from_mry(self, mry):
        for saddr, prop in self.map.recv.items():
            value = mry.read(Address(saddr))
            # log.debug(f"[{saddr}]: {prop}={value}")
            self.direct_set(prop, value.int)

    def set_mry_map(self):
        for Addr, prop in self.map.recv.items():
            prop = self.prefix + "_" + prop
            Addr = Address(Addr)+256 if self.prefix=='fx' else Addr
            # log.debug(f"[{str(Addr)}]> {prop}")
            self.device.mry.map[str(Addr)] = ( self, prop) 


