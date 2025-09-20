from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from .map import Map
from .anti_flood import AntiFlood

class ModFx(AntiFlood, GObject.GObject):
    __gsignals__ = {
        "modfx-map-ready": (GObject.SIGNAL_RUN_FIRST, None, (object,object,)),
        #"fx-map-ready":  (GObject.SIGNAL_RUN_FIRST, None, (object,)),
    }
    type_idx      = GObject.Property(type=int, default=-1)
    mod_sw        = GObject.Property(type=bool, default=False)
    mod_type      = GObject.Property(type=int, default=0)
    mod_idx       = GObject.Property(type=int, default=-1)
    mod_status    = GObject.Property(type=int, default=0)
    mod_select    = GObject.Property(type=int, default=0)
    mod_G         = GObject.Property(type=int, default=0)
    mod_R         = GObject.Property(type=int, default=0)
    mod_Y         = GObject.Property(type=int, default=0)
    fx_sw         = GObject.Property(type=bool, default=False)
    fx_type       = GObject.Property(type=int, default=0)
    fx_idx        = GObject.Property(type=int, default=-1)
    fx_status     = GObject.Property(type=int, default=0)
    fx_select     = GObject.Property(type=int, default=0)
    fx_G          = GObject.Property(type=int, default=0)
    fx_R          = GObject.Property(type=int, default=0)
    fx_Y          = GObject.Property(type=int, default=0)
    
    def __init__(self, device, ctrl, name="TouchWah"):
        super().__init__()
        self.name = name
        self.ctrl = ctrl
        self.device = device
        self.map = Map("params/touchwah.yaml")
        self.banks=['G', 'R', 'Y']

        self.mry_id = device.mry.connect("mry-loaded", self.load_from_mry)
        self.device.connect("load-maps", self.load_map)
        self.notify_id = self.connect("notify", self.set_from_ui)

    def load_map(self, ctrl):
        self.emit(self.name + "-map-ready", self.map['Types'])

    def set_mry_map(self):
        for Addr, prop in self.map.recv.items():
            self.device.mry.map[str(Addr)] = (self, prop)

    def set_from_msg(self, name, value):
        name = name.replace('-', '_')
        log.debug(f">>> {name} = {value}")
        if 'type' in name:
            svalue = to_str(value)
            num = list(self.map['Types'].values()).index(svalue)
            self.set_property(self.prefix + '_idx', num)
        else:
            self.set_property(name, value)


    def set_from_ui(self, name, value):
        name = name.replace('-', '_')
        log.debug(f">>> {name} = {value}")
        if isinstance(value, float):
            value = int(value)
        Addr = self.map.get_addr(name)
        return
        if 'sw' in name:
            value = 1 if value else 0
            self.ctrl.send(Addr, value, True)
        elif name == 'delay_type':
            num = list(self.map['Types'].values()).index(to_str(value))
            self.direct_set("type_idx", num)
        elif name == 'type_idx':
            model_val = list(self.map['Types'].values())[value]
            Addr  = self.map.send["delay_type"]
            self.ctrl.send(Addr, model_val, True)
        elif name == 'bank_select':
            self.ctrl.send(Addr, value, True)
        elif 'lvl' in name or name == 'bank_select':
            if name in ['time_lvl', 'd1_time_lvl', 'd2_time_lvl']:
                value = int_to_midi_bytes(int(value), 2)
                
                log.debug(f"{name} {Addr} {to_str(value)}")
                self.ctrl.send(Addr, value, True)
            else:
                self.ctrl.send(Addr, value, True)
        else:
            log.debug(f"missing DEF for '{name}'")

    def direct_set(self, prop, value):
        self.handler_block_by_func(self._on_any_property_changed)
        self.set_property(prop, value)
        self.handler_unblock_by_func(self._on_any_property_changed)

    def get_bank_var(self, var):
        log.debug(f"{self.delay_status=}")
        if self.delay_status == 0:
            log.warning(f"{self.delay_status=}")
            return var + self.banks[0]
        else:
            return var + self.banks[self.delay_status - 1]

    def set_bank_type(self):
        bank_name = self.get_bank_var("bank_")
        d_type = self.get_property(bank_name)
        num = list(self.map['Types'].values()).index(to_str(d_type))
        log.debug(f"{bank_name} {to_str(d_type)} idx={num}")
        self.direct_set("type_idx", num)

    def load_from_mry(self, mry):
        # log.debug("-")
        for saddr, prop in self.map.recv.items():
            value = mry.read(Address(saddr))
            if prop in ['dc_rep_lvl']:
                value = mry.read(Addr, 3)
                self.direct_set(prop, value.int)
            else:
                if value is not None and value >= 0:
                    self.direct_set(prop, value.int)
        self.set_bank_type()


