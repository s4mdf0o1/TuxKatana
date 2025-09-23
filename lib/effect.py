from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from .midi_bytes import Address, MIDIBytes

from .map import Map

class Effect:
    def __init__(self, name, device, parent_prefix="" ):
        super().__init__()
        self.name = name
        self.parent_prefix = parent_prefix
        self.is_modfx = True if self.parent_prefix else False
        self.prefix = self.get_prefix()
        # log.debug(self.prefix)
        self.signal_name = self.get_signal_name()
        self.ctrl = device.ctrl
        self.device = device
        # self.is_modfx = is_modfx
        self.params_file = self.get_params_file(name)
        self.map = Map( self.params_file )
        self.set_mry_map()
        self.banks=['G', 'R', 'Y']

        self.mry_id = device.mry.connect("mry-loaded", self.load_from_mry)
        device.connect("load-maps", self.load_map)
        self.notify_id = self.connect("notify", self.set_from_ui)

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
            if not (self.prefix == 'mo_' and 'fx_' in prop)\
                    and not (self.prefix == 'fx_' and 'mo_' in prop):
                self.device.mry.map[str(Addr)] = ( self, prop )
            # else:
                # log.debug(f"{prop}: {Addr}")

    def direct_set(self, prop, value):
        log.debug(prop)
        # self.handler_block_by_func(self.set_from_ui)
        self.handler_block(self.notify_id)
        self.set_property(prop, value)
        self.handler_unblock(self.notify_id)
        # self.handler_unblock_by_func(self.set_from_ui)

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

    def get_params_file(self, name):
        pf = ""
        if name in ['Mod', 'Fx']:
            pf = "params/modfx.yaml"
        elif self.is_modfx:
            pf = f"params/modfx/{name.lower().replace(' ', '_')}.yaml"
        else:
            pf = f"params/{name.lower()}.yaml"
        return pf

    def set_from_msg(self, name, value):
        name = name.replace('-', '_')
        log.debug(f">>> {name} = {value}")
        self.direct_set(name, value)

    def set_from_ui(self, obj, pspec):
        name = pspec.name.replace('-','_')
        value = self.get_property(name)
        # log.debug(f"{name}={value} {self.prefix=}")
        name = name.replace('-','_')
        # log.debug(f"{self.map}")
        prop = self.parent_prefix+name
        Addr = self.search_addr(prop)
        # log.debug(f">>> [{Addr}]> {prop} {name}={value}")
        if isinstance(value, float):
            value = int(value)
        if '_idx' in name:
            key = 'Types' if 'type' in name else 'Modes'
            prop= name.replace('_idx', '')
            if self.is_modfx:
                log.debug("is_modfx")
                prop = self.parent_prefix + prop
            model_val = list(self.map[ key ].values())[value]
            Addr  = self.search_addr(prop)
            if Addr:
                self.ctrl.send(Addr, model_val, True)
            else:
                log.debug(f"{prop} Addr not found in self.map")
        if '_lvl' in name:
            if Addr:
                self.ctrl.send(Addr, value, True)
        elif not Addr:
            log.warning(f"{name} not found in device.mry.map")

    def get_bank_var(self):
        status = self.get_property(self.prefix+'status')
        bank_var = self.banks[status - 1] if status else self.banks[0]
        return self.prefix + 'bank_' + bank_var
 
