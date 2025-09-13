from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from .tools import to_str, from_str, int_to_midi_bytes

from .map import Map
from .anti_flood import AntiFlood

class Delay(AntiFlood, GObject.GObject):
    __gsignals__ = {
        "delay-map-ready": (GObject.SIGNAL_RUN_FIRST, None, (object,)),
    }
    delay_sw        = GObject.Property(type=bool, default=False)
    delay_type      = GObject.Property(type=int, default=0)
    type_idx        = GObject.Property(type=int, default=0)
    delay_status    = GObject.Property(type=int, default=0)
    bank_select     = GObject.Property(type=int, default=0)
    bank_G          = GObject.Property(type=int, default=0)
    bank_R          = GObject.Property(type=int, default=0)
    bank_Y          = GObject.Property(type=int, default=0)
    time_lvl        = GObject.Property(type=float, default=0.0)
    feedback_lvl    = GObject.Property(type=float, default=0.0)
    tap_time_lvl    = GObject.Property(type=float, default=0.0)
    high_cut_lvl    = GObject.Property(type=float, default=0.0)
    effect_lvl      = GObject.Property(type=float, default=0.0)
    dirmix_lvl      = GObject.Property(type=float, default=0.0)
    d1_time_lvl     = GObject.Property(type=float, default=0.0)
    d1_fb_lvl       = GObject.Property(type=float, default=0.0)
    d1_h_cut_lvl    = GObject.Property(type=float, default=0.0)
    d1_eff_lvl      = GObject.Property(type=float, default=0.0)
    d2_time_lvl     = GObject.Property(type=float, default=0.0)
    d2_fb_lvl       = GObject.Property(type=float, default=0.0)
    d2_h_cut_lvl    = GObject.Property(type=float, default=0.0)
    d2_eff_lvl      = GObject.Property(type=float, default=0.0)
    mod_rate_lvl    = GObject.Property(type=float, default=0.0)
    mod_depth_lvl   = GObject.Property(type=float, default=0.0)
    sde_vint_lpf_sw = GObject.Property(type=bool, default=False)
    sde_fb_phase_sw = GObject.Property(type=bool, default=False)
    sde_ef_phase_sw = GObject.Property(type=bool, default=False)
    sde_filter_sw   = GObject.Property(type=bool, default=False)
    sde_modul_sw    = GObject.Property(type=bool, default=False)

    def __init__(self, device, ctrl):
        super().__init__()
        self.name = "Delay"
        self.ctrl = ctrl
        self.device = device

        self.map = Map("params/delay.yaml")
        self.set_mry_map()

        self.banks=['G', 'R', 'Y']

        self.notify_id = self.connect("notify", self._on_any_property_changed)
        self.mry_id = device.mry.connect("mry-loaded", self.load_from_mry)

        self.device.connect("load-maps", self.load_map)

    def load_map(self, ctrl):
        self.emit("delay-map-ready", self.map['Types'])

    def on_param_changed(self, name, value):
        name = name.replace('-', '_')
        log.debug(f">>> {name} = {value}")
        if not isinstance(value, (int, bool, float)):
            value = from_str(value)
        if isinstance(value, float):
            value = int(value)
        addr = self.map.get_addr(name)
        if 'sw' in name:
            value = 1 if value else 0
            #log.debug(f"{name} {to_str(addr)} {to_str(value)}")
            self.device.send(addr, [value])
        elif name == 'delay_status':
            self.direct_set(name, value)
        elif name == 'delay_type':
            num = list(self.map['Types'].values()).index(to_str(value))
            self.direct_set("type_idx", num)
        elif name == 'type_idx':
            model_val = list(self.map['Types'].values())[value]
            addr  = self.map.send["delay_type"]
            #log.debug(f"{name} {addr} {model_val}")
            self.device.send(from_str(addr), from_str(model_val))
        #elif 'mode' in name and name.split('_')[1] in self.banks:
        #    num = list(self.map['Modes'].values()).index(to_str(value))
        #    self.direct_set("mode_idx", num)
        #elif name == 'mode_idx':
        #    mode_val = list(self.map['Modes'].values())[value]
        #    bank = self.get_bank_var("mode_")
        #    addr  = self.map.send[bank]
        #    self.device.send(from_str(addr), from_str(mode_val))
        elif name == 'bank_select':
            self.device.send(addr, [value])
        elif 'lvl' in name or name == 'bank_select':
            if name in ['time_lvl', 'dly1_time_lvl', 'dly2_time_lvl']:
                value = int_to_midi_bytes(value, 2)
                
                #log.debug(f"{name} {to_str(addr)} {to_str(value)}")
                self.device.send(addr, value)
            else:
                #log.debug(f"{name} {to_str(addr)} {to_str(value)}")
                self.device.send(addr, [value])
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
        log.debug("-")
        for addr, prop in self.map.recv.items():
            value = mry.read_from_str(addr)
            #log.debug(f"{prop}: {addr} = {to_str(value)}")
            if prop in ['time_lvl', 'd1_time_lvl']:
                value = mry.read_from_str(addr, 2)
                self.direct_set(prop, value)
            else:
                if value is not None and value >= 0:
                    self.direct_set(prop, value)
        self.set_bank_type()

    def set_mry_map(self):
        for addr, prop in self.map.recv.items():
            self.device.mry.map[addr] = ( self, prop ) 


