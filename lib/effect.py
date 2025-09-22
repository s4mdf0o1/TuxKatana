from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from .midi_bytes import Address, MIDIBytes

from .map import Map

class Effect:
    def __init__(self, device, ctrl, name):
        super().__init__()
        self.name = name
        self.ctrl = ctrl
        self.device = device
        self.map = Map(f"params/{name.lower()}.yaml")
        self.set_mry_map()

        self.mry_id = device.mry.connect("mry-loaded", self.load_from_mry)
        self.device.connect("load-maps", self.load_map)

    def load_map(self, ctrl):
        self.emit(f"{self.name.lower()}-map-ready", self.map)

    def set_mry_map(self):
        for Addr, prop in self.map.recv.items():
            self.device.mry.map[str(Addr)] = ( self, prop )

    def direct_set(self, prop, value):
        # log.debug(prop)
        self.handler_block_by_func(self.set_from_ui)
        self.set_property(prop, value)
        self.handler_unblock_by_func(self.set_from_ui)

    def load_from_mry(self, mry):
        for saddr, prop in self.map.recv.items():
            value = mry.read(Address(saddr))
            # log.debug(f"[{saddr}]: {prop}={value}")
            self.direct_set(prop, value.int)
        # log.debug(f"{self.device.mry.map}") 



