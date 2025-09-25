from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from .midi_bytes import Address, MIDIBytes

from .map import Map

class Effect:
    def __init__(self, ctrl, mapping, parent_prefix=""):
        super().__init__()
        self.ctrl = ctrl
        self.mry = ctrl.mry
        self.mapping = mapping
        self.parent_prefix = parent_prefix
        self.is_modfx = True if self.parent_prefix else False
        # self.signal_name = self.get_signal_name()
        # self.set_mry_map()
        # self.banks=['G', 'R', 'Y']
        self.status_bind = False

        self.notify_id = self.connect("notify", self.on_ui_changed)
        self.mry_id = self.mry.connect("address-changed", self.on_mry_changed)
        self.mry.connect("mry-loaded", self.on_mry_loaded)

    def on_mry_changed(self, mry, addr, val):# name, value):
        prop = self.mapping.inverse.get(addr, None)
        if not prop:
            return
        # log.debug(f"{addr=} {val=} {prop=}")
        current = getattr(self, prop, None)
        # log.debug(f"{addr=} {prop} {current=} {val=}")
        if current != val:
            self.direct_set(prop, val)

    def on_ui_changed(self, obj, pspec):
        name = pspec.name.replace('-','_')
        log.debug(name)
        value = obj.get_property(pspec.name)
        # log.debug(f"{type(self.get_property(name))=}")
        # addr = Address()
        value = self.type_val(name, value)
        current = None
        if not name in self.mapping:
            # log.warning(f"{name} not in mapping")
            if '_idx' in name:
                store = self.types if 'type' in name else self.modes
                prop = name.replace('_idx', '')
                if self.is_modfx:
                    prop = self.parent_prefix + prop
                value = getattr(self, prop)
                model_val = list(store.inverse)[value]
                addr = self.mapping[prop]
                current = self.mry.get_value(addr)
                log.debug(f"{name=} {prop=} {addr=} {value=} {current=}")
                if current != value:
                    return
                    self.mry.set_value(addr, value)

                return
        else:
            addr = self.mapping[name]
            val_type = pspec.value_type.name
            current = self.mry.get_value(addr)
            cur_type = type(current)
            log.debug(f"{name}={value}({val_type})/{current}({cur_type})")
        if '_status' in name and not self.status_bind:
            self.ctrl.emit('status-changed')
        value = self.get_property(name)
        # log.debug(f"{name}={value} {self.prefix=}")
        name = self.parent_prefix+name
        if name in self.mapping:
            addr = self.mapping[name]
            val = MIDIBytes(getattr(self, name))
            current = self.mry.get_value(addr)
            # log.debug(f"{name=} {addr=} {val=} {current=}")
            if current != val:
                self.direct_mry(addr, val.int)

    def direct_set(self, prop, value):
        # log.debug(f"{prop}={value}")
        if '_status' in prop and not self.status_bind:
            log.debug(f"{prop}={value}")
            self.ctrl.emit('status-changed', self, prop)
            self.status_bind=True
        value = self.type_val(prop, value)
        self.handler_block(self.notify_id)
        self.set_property(prop, value)
        self.handler_unblock(self.notify_id)

    def direct_mry(self, addr, val):
        # log.debug(f"{addr}={val}")
        self.mry.handler_block(self.mry_id)
        self.mry.set_value(addr, val)
        self.mry.handler_unblock(self.mry_id)

    def on_mry_loaded(self, mry):
        # log.debug("load mry")
        for prop, addr in self.mapping.items():
            val = mry.read(addr)
            # log.debug(f"{addr}: {prop}={val}")
            # val = self.type_val(prop, val)
            if val != None:
                self.direct_set(prop, val)
            # else:
                # log.debug(f"{prop}: val is None")

    def type_val(self, prop, val):
        val_type = self.find_property(prop).value_type.name
        if val is None:
            return val
        if val_type == 'gboolean' and type(val)!=bool:
            val = val.bool
        elif val_type == 'gint' and type(val) != int:
            val = val.int
        return val

    # def on_ui_change(self, obj, pspec):
    #     prop = pspec.name.replace('-', '_')
    #     if prop in self._mapping:
    #         addr = self._mapping[prop]
    #         val = getattr(self, prop)
    #         current = self.mry.get_value(addr)
    #         log.debug(f"{prop=} {addr=} {val=} {current=}")
    #         if current != val:
    #             self.mry.set_value(addr, val)


#    def set_mry(self, prop, value):
#        log.debug(f"{prop}={value}")
        # self.handler_block_by_func(self.set_from_ui)
#        self.handler_block(self.mry_id)
#        self.set_property(prop, value)
#        self.handler_unblock(self.mry_id)
 


        # Addr = self.search_addr(prop)
        # # log.debug(f">>> [{Addr}]> {prop} {name}={value}")
        # if isinstance(value, float):
        #     value = int(value)
        # if '_idx' in name:
        #     key = 'Types' if 'type' in name else 'Modes'
        #     prop= name.replace('_idx', '')
        #     if self.is_modfx:
        #         log.debug("is_modfx")
        #         prop = self.parent_prefix + prop
        #     model_val = list(self.map[ key ].values())[value]
        #     Addr  = self.search_addr(prop)
        #     if Addr:
        #         self.ctrl.send(Addr, model_val, True)
        #     else:
        #         log.debug(f"{prop} Addr not found in self.map")
        # if '_lvl' in name:
        #     if Addr:
        #         self.ctrl.send(Addr, value, True)
        # elif not Addr:
        #     log.warning(f"{name} not found in ctrl.mry.map")


# #####

    # def get_signal_name(self):
        # if self.name in ['Mod', 'Fx']:
        #     return "modfx-map-ready"
        # return ''.join(self.name.lower().split()) + "-map-ready"

    # def load_map(self, ctrl):
        # self.emit(self.signal_name, self.map)

    # def set_mry_map(self):
        # for Addr, prop in self.map.recv.items():
        #     if self.is_modfx:
        #         prop = self.parent_prefix + prop
        #         Addr = Address(Addr)+256 \
        #                 if self.parent_prefix=='fx_' else Addr
        #     if not (self.prefix == 'mo_' and 'fx_' in prop)\
        #             and not (self.prefix == 'fx_' and 'mo_' in prop):
        #         self.ctrl.mry.map[str(Addr)] = ( self, prop )
        #     # else:
        #         # log.debug(f"{prop}: {Addr}")

    # def load_from_mry(self, mry):
    #     for saddr, prop in self.map.recv.items():
    #         if self.name in ['Mod', 'Fx'] \
    #                 and not prop[:3] in ['mo_', 'fx_']:
    #             prop = self.prefix + prop
    #         value = mry.read(Address(saddr))
    #         # log.debug(f"[{saddr}]: {prop}={value}")
    #         if hasattr(self, prop):
    #             self.direct_set(prop, value.int)
    #         else:
    #             log.warning(f"{self.name} has no '{prop}' property")
    #     # log.debug(f"{self.mry.map}") 

    # def search_addr(self, prop):
    #     for k, v in self.ctrl.mry.map.items():
    #         o, p = v
    #         # log.debug(f"{prop} {o.name} {p}")
    #         if p == prop:
    #             return k

    # def get_params_file(self, name):
    #     pf = ""
    #     if name in ['Mod', 'Fx']:
    #         pf = "params/modfx.yaml"
    #     elif self.is_modfx:
    #         pf = f"params/modfx/{name.lower().replace(' ', '_')}.yaml"
    #     else:
    #         pf = f"params/{name.lower()}.yaml"
    #     return pf

    # def get_bank_var(self):
    #     status = self.get_property(self.prefix+'status')
    #     bank_var = self.banks[status - 1] if status else self.banks[0]
    #     return self.prefix + 'bank_' + bank_var
 
