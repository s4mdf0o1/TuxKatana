from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from .map import Map
from .midi_bytes import Address, MIDIBytes

class ModFx(GObject.GObject):
    __gsignals__ = {
        "modfx-map-ready": (GObject.SIGNAL_RUN_FIRST, None, (object,)),
        #"fx-map-ready":  (GObject.SIGNAL_RUN_FIRST, None, (object,)),
    }
    type_idx    = GObject.Property(type=int, default=-1)
    mod_sw      = GObject.Property(type=bool, default=False)
    mod_type    = GObject.Property(type=int, default=0)
    mod_idx     = GObject.Property(type=int, default=-1)
    mod_bank_G  = GObject.Property(type=int, default=0)
    mod_bank_R  = GObject.Property(type=int, default=0)
    mod_bank_Y  = GObject.Property(type=int, default=0)
    mod_bank_sel= GObject.Property(type=int, default=0)
    mod_status  = GObject.Property(type=int, default=0)
    mod_vol_lvl = GObject.Property(type=int, default=0)
    fx_sw       = GObject.Property(type=bool, default=False)
    fx_type     = GObject.Property(type=int, default=0)
    fx_idx      = GObject.Property(type=int, default=-1)
    fx_bank_G   = GObject.Property(type=int, default=0)
    fx_bank_R   = GObject.Property(type=int, default=0)
    fx_bank_Y   = GObject.Property(type=int, default=0)
    fx_bank_sel = GObject.Property(type=int, default=0)
    fx_status   = GObject.Property(type=int, default=0)
    fx_vol_lvl  = GObject.Property(type=int, default=0)
    #mod_unknown_1 = GObject.Property(type=int, default=0)
    #fx_unknown_1  = GObject.Property(type=int, default=0)
    
    def __init__(self, device, ctrl, name):
        super().__init__()
        self.name = name
        self.prefix = name.lower() + '_'
        # log.debug(f">>>>>> {name}, {self.prefix}<<<<<<<<<<<")
        self.ctrl = ctrl
        self.device = device
        self.map = Map("params/modfx.yaml")
        self.set_mry_map()
        self.banks=['G', 'R', 'Y']

        self.libs={}

        self.mry_id = device.mry.connect("mry-loaded", self.load_from_mry)
        self.device.connect("load-maps", self.load_map)
        self.notify_id = self.connect("notify", self.set_from_ui)

    def load_map(self, ctrl):
        self.emit("modfx-map-ready", self.map['MFTypes'])

    def set_mry_map(self):
        for Addr, prop in self.map.recv.items():
            if self.prefix in prop:
                self.device.mry.map[str(Addr)] = (self, prop)
    def set_from_msg(self, name, value):
        name = name.replace('-', '_')
        log.debug(f">>> {name} = {value}, {type(value)}")
        # log.debug(f"{self.setting=}")
        if name == self.prefix + 'type':
            svalue = str(MIDIBytes(value))
            num = list(self.map['MFTypes'].values()).index(svalue)
            self.direct_set(self.prefix + 'idx', num)
        elif name == self.prefix + 'status':
            self.direct_set(name, value)
            bank_prop = self.get_bank_var()
            log.debug(f"{bank_prop}: {self.get_property(bank_prop)}")
            bank_val = self.get_property(bank_prop)
            self.direct_set("type_idx", bank_val )
            # self.type_idx = bank_val
        elif '_vol_lvl' in name or 'bank' in name:
            self.direct_set(name, value)
        else:
            log.warning(f"NEED PRECISE: {name}={value}")
            # self.direct_set(name, value)

    def set_from_ui(self, obj, pspec):
        name = pspec.name
        value = self.get_property(name)
        name = name.replace('-', '_')
        log.debug(f">>> {name} = {value} ({self.prefix})")
        if isinstance(value, float):
            value = int(value)
        Addr = self.map.get_addr(name)
        # if name == self.prefix + 'idx':
        if 'idx' in name:# == self.prefix + 'idx':
            log.debug(f"{name=}")
            type_val = list(self.map['MFTypes'].values())[value]
            Addr  = self.map.send[self.prefix + "type"]
            self.ctrl.send(Addr, type_val, True)
        elif name == self.prefix + 'bank_sel':
            self.ctrl.send(Addr, value, True)
        elif 'sw' in name:
            value = 1 if value else 0
            self.ctrl.send(Addr, value, True)
            #else:
            #    self.ctrl.send(Addr, value, True)
        elif self.prefix+"bank_" in name or '_vol_lvl' in name:
            log.debug(f"{name}: {Addr}: {value}")
            self.ctrl.send(Addr, value, True)
        else:
            log.debug(f"missing DEF for '{name}'")

    def direct_set(self, prop, value):
        if 'unknown' in prop or \
                not hasattr(self, prop):
            # log.warning(f"ModFx: Unknown Property: {prop}={value}")
            return
        log.debug(f"{prop}={value}")
        self.handler_block_by_func(self.set_from_ui)
        self.set_property(prop, value)
        self.handler_unblock_by_func(self.set_from_ui)

    def get_bank_var(self):
        status = self.get_property(self.prefix+'status')
        bank_var = self.banks[status - 1] if status else self.banks[0]
        return self.prefix + 'bank_' + bank_var
    
    def set_bank_type(self):
        bank_name = self.get_bank_var()
        d_type = self.get_property(bank_name)
        d_type = str(MIDIBytes(d_type))
        num = list(self.map['MFTypes'].values()).index(d_type)
        self.direct_set("type_idx", num)

    def load_from_mry(self, mry):
        #log.debug(self.map.recv.items())
        for saddr, prop in self.map.recv.items():
            value = mry.read(Address(saddr))
            # log.debug(f"{saddr} {value.int=}")
            if value is not None and value.int >= 0:
                self.direct_set(prop, value.int)
        self.set_bank_type()


