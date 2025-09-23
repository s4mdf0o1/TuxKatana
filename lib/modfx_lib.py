from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from .map import Map
from .effect import Effect
from .midi_bytes import Address, MIDIBytes

class ModFx(Effect, GObject.GObject):
    __gsignals__ = {
        "modfx-map-ready": (GObject.SIGNAL_RUN_FIRST, None, (object,)),
        #"fx-map-ready":  (GObject.SIGNAL_RUN_FIRST, None, (object,)),
    }
    type_idx    = GObject.Property(type=int, default=-1)
    mo_sw      = GObject.Property(type=bool, default=False)
    mo_type    = GObject.Property(type=int, default=0)
    mo_idx     = GObject.Property(type=int, default=-1)
    mo_bank_G  = GObject.Property(type=int, default=0)
    mo_bank_R  = GObject.Property(type=int, default=0)
    mo_bank_Y  = GObject.Property(type=int, default=0)
    mo_bank_sel= GObject.Property(type=int, default=0)
    mo_status  = GObject.Property(type=int, default=0)
    mo_vol_lvl = GObject.Property(type=int, default=0)
    fx_sw       = GObject.Property(type=bool, default=False)
    fx_type     = GObject.Property(type=int, default=0)
    fx_idx      = GObject.Property(type=int, default=-1)
    fx_bank_G   = GObject.Property(type=int, default=0)
    fx_bank_R   = GObject.Property(type=int, default=0)
    fx_bank_Y   = GObject.Property(type=int, default=0)
    fx_bank_sel = GObject.Property(type=int, default=0)
    fx_status   = GObject.Property(type=int, default=0)
    fx_vol_lvl  = GObject.Property(type=int, default=0)
    #mo_unknown_1 = GObject.Property(type=int, default=0)
    #fx_unknown_1  = GObject.Property(type=int, default=0)
    
    def __init__(self, device, name):
        super().__init__(name, device )
         ## DEBUG Memory MAP Dict
        # mry_map = self.device.mry.map.copy()
        # for k, v in mry_map.items():
        #     obj, prop = v
        #     mry_map[k]= prop
        # with open(self.prefix+"map.log", 'w') as f:
        #     yaml.dump(mry_map, f)
        self.libs={}

        self.notify_id = self.connect("notify", self.set_from_ui)

    def set_from_msg(self, name, value):
        name = name.replace('-', '_')
        # log.debug(f">>> {name} = {value}, {self.prefix} {self.name}")
        # log.debug(f"{self.setting=}")
        log.debug(f"{self.prefix+'type'=}")
        if name == self.prefix + 'type' or 'bank' in name:
            svalue = str(MIDIBytes(value))
            num = list(self.map['Types'].values()).index(svalue)
            log.debug(f"{num=}")
            self.direct_set(self.prefix + 'idx', num)
        elif name == self.prefix + 'status':
            self.direct_set(name, value)
            bank_prop = self.get_bank_var()
            # log.debug(f"{bank_prop}: {self.get_property(bank_prop)}")
            bank_val = self.get_property(bank_prop)
            self.direct_set("type_idx", bank_val )
        elif '_vol_lvl' in name:
            self.direct_set(name, value)
        else:
            log.warning(f"NEED PRECISE: {name}={value}")

    def set_from_ui(self, obj, pspec):
        name = pspec.name
        value = self.get_property(name)
        name = name.replace('-', '_')
        # log.debug(f">>> {name} = {value} ({self.prefix})")
        if isinstance(value, float):
            value = int(value)
        Addr = self.map.get_addr(name)
        if 'idx' in name:
            type_val = list(self.map['Types'].values())[value]
            # if value == 5 and type_val == '06':
            #     log.debug(f"{self.map=} {type(type_val)=}")
            Addr  = self.map.send[self.prefix + "type"]
            self.ctrl.send(Addr, type_val, True)
        elif name == self.prefix + 'bank_sel':
            # log.debug(f"{name=} {value}")
            self.ctrl.send(Addr, value, True)
        elif 'sw' in name:
            value = 1 if value else 0
            self.ctrl.send(Addr, value, True)
        elif self.prefix+"bank_" in name or 'vol_lvl' in name:
            # log.debug(f"{name}: {Addr}: {value}")
            self.ctrl.send(Addr, value, True)
        else:
            log.debug(f"missing DEF for '{name}'")

    def get_bank_var(self):
        status = self.get_property(self.prefix+'status')
        bank_var = self.banks[status - 1] if status else self.banks[0]
        return self.prefix + 'bank_' + bank_var
    
    def set_bank_type(self):
        bank_name = self.get_bank_var()
        d_type = self.get_property(bank_name)
        d_type = str(MIDIBytes(d_type))
        num = list(self.map['Types'].values()).index(d_type)
        self.direct_set("type_idx", num)


