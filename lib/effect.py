from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from .midi_bytes import Address, MIDIBytes

class Effect:
    def __init__(self, ctrl, mapping, pprefx=""):

        super().__init__()
        self.ctrl = ctrl
        self.mry = ctrl.mry
        self.mapping = mapping
        self.parent_prefix = pprefx
        self.is_modfx = True if pprefx else False
        self.status_bind = False

        self.notify_id = self.connect("notify", self.on_ui_changed)
        self.mry.connect("mry-loaded", self.on_mry_loaded)
        self.mry_id = self.mry.connect("address-changed", self.on_mry_changed)

    def on_mry_changed(self, mry, addr, val):# name, value):
        prop = self.mapping.inverse.get(addr, None)
        if not prop:
            return
        log.debug(f"{addr=} {val=} {prop=}")
        current = getattr(self, prop, None)
        # log.debug(f"{addr=} {prop} {current=} new val:{self.type_val(prop,val)}")
        if current != val:
            self.direct_set(prop, val)

    def on_ui_changed(self, obj, pspec):
        name = pspec.name.replace('-','_')
        if not name in self.mapping and not '_idx' in name:
            # log.warning(name)
            return
        value = obj.get_property(name)
        addr = self.mapping.get(name, None)
        current = None
        if addr:
            current = self.mry.read(addr)
        log.debug(f"{self.name} | {addr}: {name}={value} / {current=}")
        if name == self.name.lower() + '_sw'\
                or name.endswith('_bank_sel'):
            self.direct_mry(addr, value)
        elif name.endswith('_status') and not self.status_bind:
            self.ctrl.emit('status-changed', self, name)
        elif name.endswith('_idx') and 'type' in name:
            name = name.replace('_idx', '')
            value = list(self.types.inverse)[value]
            current = self.get_property(name)
            addr = self.mapping.get(name, None)
        # log.debug(f"{name}={value} {self.prefix=}")
            if current != value:
                self.direct_mry(addr, value)
        elif name.endswith('_lvl'):
            # log.debug(f"{name}={value}/{current}")
            if current != value:
                self.direct_mry(addr, value)

    def direct_set(self, prop, value):
        # log.debug(f"{prop}={value}:{type(value)}")
        value = self.type_val(prop, value)
        # log.debug(f"{prop}={value}:{type(value)}")
        self.handler_block(self.notify_id)
        self.set_property(prop, value)
        self.handler_unblock(self.notify_id)
        if '_status' in prop and not self.status_bind:
            # log.debug(f"{prop}={value}/{self.get_property(prop)}")
            self.ctrl.emit('status-changed', self, prop)
            self.status_bind=True

    def direct_mry(self, addr, val):
        if self.parent_prefix == 'fx_':
            addr += 256
        # log.debug(f"{addr}={val}({type(val)}) {self.parent_prefix} {self.is_modfx}")
        self.mry.handler_block(self.mry_id)
        self.mry.set_value(addr, val)
        self.mry.handler_unblock(self.mry_id)

    def on_mry_loaded(self, mry):
        # log.debug("load mry")
        for prop, addr in self.mapping.items():
            val = mry.read(addr)
            if val != None:
                self.direct_set(prop, val)
            else:
                log.warning("{prop}: {val=}")
       

    def type_val(self, prop, val):
        # log.debug(f"{prop=} {val=}")
        val_type = self.find_property(prop).value_type.name
        # log.debug(val_type)
        if isinstance(val, MIDIBytes):
            return val.to_gtype(val_type)
        return val

