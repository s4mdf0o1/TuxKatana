from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from .midi_bytes import Address, MIDIBytes

from .map import Map

class Reverb(GObject.GObject):
    __gsignals__ = {
        "reverb-map-ready": (GObject.SIGNAL_RUN_FIRST, None, (object,object,)),
    }
    reverb_sw       = GObject.Property(type=bool, default=False)
    reverb_type     = GObject.Property(type=int, default=0)
    type_idx        = GObject.Property(type=int, default=0)
    reverb_status   = GObject.Property(type=int, default=0)
    bank_select     = GObject.Property(type=int, default=0)
    bank_G          = GObject.Property(type=int, default=0)
    bank_R          = GObject.Property(type=int, default=0)
    bank_Y          = GObject.Property(type=int, default=0)
    mode_idx        = GObject.Property(type=int, default=0)
    mode_G          = GObject.Property(type=int, default=0)
    mode_R          = GObject.Property(type=int, default=0)
    mode_Y          = GObject.Property(type=int, default=0)
    pre_delay_lvl   = GObject.Property(type=float, default=0.0)
    time_lvl        = GObject.Property(type=float, default=0.0)
    density_lvl     = GObject.Property(type=float, default=0.0)
    low_cut_lvl     = GObject.Property(type=float, default=0.0)
    high_cut_lvl    = GObject.Property(type=float, default=0.0)
    effect_lvl      = GObject.Property(type=float, default=0.0)
    dir_mix_lvl     = GObject.Property(type=float, default=0.0)

    def __init__(self, device, ctrl):
        super().__init__()
        self.name = "Reverb"
        self.ctrl = ctrl
        self.device = device
        self.map = Map("params/reverb.yaml")
        self.set_mry_map()

        self.banks=['G', 'R', 'Y']

        self.notify_id = self.connect("notify", self.set_from_ui)
        self.mry_id = device.mry.connect("mry-loaded", self.load_from_mry)

        self.device.connect("load-maps", self.load_map)

    def load_map(self, ctrl):
        self.emit("reverb-map-ready", self.map['ReverbTypes'], self.map['Modes'])

    def set_from_msg(self, name, value):
        name = name.replace('-', '_')
        # log.debug(f">>> {name} = {value}")
        if name == 'reverb_type':
            svalue = str(MIDIBytes(value))
            num = list(self.map['ReverbTypes'].values()).index(svalue)
            self.direct_set("type_idx", num)
        else:
            self.direct_set(name, value)

    def set_from_ui(self, obj, pspec):
        name = pspec.name
        value = self.get_property(name)
        name = name.replace('-', '_')
        # log.debug(f">>> {name} = {value}")
        if isinstance(value, float):
            value = int(value)
        Addr = self.map.get_addr(name)
        if name == 'type_idx':
            model_val = list(self.map['ReverbTypes'].values())[value]
            Addr  = self.map.get_addr("reverb_type")
            self.ctrl.send(Addr, model_val, True)
        elif name == 'mode_idx':
            mode_val = list(self.map['Modes'].values())[value]
            bank = self.get_bank_var("mode_")
            Addr  =  self.map.get_addr(bank)
            self.ctrl.send(Addr, mode_val, True)
        elif 'lvl' in name or name == 'bank_select':
            if name == 'pre_delay_lvl':
                value = MIDIBytes(value, 2)
                self.ctrl.send(Addr, value, True)
            else:
                self.ctrl.send(Addr, value, True)
        elif 'sw' in name:
            value = 1 if value else 0
            self.ctrl.send(Addr, value, True)

    def direct_set(self, prop, value):
        self.handler_block_by_func(self.set_from_ui)
        self.set_property(prop, value)
        self.handler_unblock_by_func(self.set_from_ui)

    def get_bank_var(self, var):
        if self.reverb_status <= 0:
            log.warning(f"{self.reverb_status=}")
            return var + self.banks[0]
        else:
            return var + self.banks[self.reverb_status - 1]
        return var+bank

    def set_bank_type(self):
        bank_name = self.get_bank_var("bank_")
        r_type = self.get_property(bank_name)
        r_type = str(MIDIBytes(r_type))
        num = list(self.map['ReverbTypes'].values()).index(r_type)
        self.direct_set("type_idx", num)

    def set_bank_mode(self):
        bank_name = self.get_bank_var("mode_")
        mode = self.get_property(bank_name)
        mode = str(MIDIBytes(mode))
        num = list(self.map['Modes'].values()).index(mode)
        self.direct_set("mode_idx", num)


    def load_from_mry(self, mry):
        for saddr, prop in self.map.recv.items():
            value = mry.read(Address(saddr))
            if prop == 'pre_delay_lvl':
                value = mry.read(Address(saddr), 2)
                self.direct_set(prop, value.int)
            else:
                if value is not None and value.int >= 0:
                    self.direct_set(prop, value.int)
        self.set_bank_type()
        self.set_bank_mode()

    def set_mry_map(self):
        for Addr, prop in self.map.recv.items():
            self.device.mry.map[str(Addr)] = ( self, prop) 


