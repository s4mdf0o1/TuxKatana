from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from .midi_bytes import Address, MIDIBytes

from .map import Map

class Effect:
    def __init__(self, device, ctrl, name, is_modfx=False, parent_prefix=""):
        super().__init__()
        self.name = name
        self.parent_prefix = parent_prefix
        self.prefix = self.get_prefix()
        log.debug(self.prefix)
        self.signal_name = self.get_signal_name()
        self.ctrl = ctrl
        self.device = device
        self.is_modfx = is_modfx
        if name in ['Mod', 'Fx']:
            self.map = Map(f"params/modfx.yaml")
        elif is_modfx:
            yf = f"params/modfx/{name.lower().replace(' ', '_')}.yaml"
            self.map = Map(yf)
            # f"params/modfx/{name.lower().replace(' ', '_')}.yaml")
        else:
            self.map = Map(f"params/{name.lower()}.yaml")
        self.set_mry_map()
        self.banks=['G', 'R', 'Y']

        self.mry_id = device.mry.connect("mry-loaded", self.load_from_mry)
        self.device.connect("load-maps", self.load_map)

    def get_prefix(self):
        lower = self.name.lower()
        return lower[:2]+'_' if len(lower.split())==1 \
                else ''.join(v[:1] for v in lower.split())+'_'

    def get_signal_name(self):
        if self.name in ['Mod', 'Fx']:
            return "modfx-map-ready"
        return ''.join(self.name.lower().split()) + "-map-ready"

    def load_map(self, ctrl):
        self.emit(self.signal_name, self.map)

    def set_mry_map(self):
        for Addr, prop in self.map.recv.items():
            if self.is_modfx:
                prop = self.parent_prefix + prop
                Addr = Address(Addr)+256 \
                        if self.parent_prefix=='fx_' else Addr
                log.debug(f"{prop}: {Addr}")
            if not (self.prefix == 'mo_' and 'fx_' in prop)\
                    and not (self.prefix == 'fx_' and 'mo_' in prop):
                self.device.mry.map[str(Addr)] = ( self, prop )

    def direct_set(self, prop, value):
        # log.debug(prop)
        self.handler_block_by_func(self.set_from_ui)
        self.set_property(prop, value)
        self.handler_unblock_by_func(self.set_from_ui)

    def load_from_mry(self, mry):
        for saddr, prop in self.map.recv.items():
            if self.name in ['Mod', 'Fx'] \
                    and not prop[:3] in ['mo_', 'fx_']:
                prop = self.prefix + prop
            value = mry.read(Address(saddr))
            # log.debug(f"[{saddr}]: {prop}={value}")
            if hasattr(self, prop):
                self.direct_set(prop, value.int)
            else:
                log.warning(f"{self.name} has no '{prop}' property")
        # log.debug(f"{self.device.mry.map}") 

    def search_addr(self, prop):
        for k, v in self.device.mry.map.items():
            o, p = v
            # log.debug(f"{prop} {o.name} {p}")
            if p == prop:
                return k

