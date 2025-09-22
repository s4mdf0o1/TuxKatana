from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from .midi_bytes import Address, MIDIBytes

from .map import Map
from .effect import Effect

class Amplifier(Effect, GObject.GObject):
    __gsignals__ = {
        "amplifier-map-ready": (GObject.SIGNAL_RUN_FIRST, None, (object,)),
    }
    amp_num     = GObject.Property(type=int, default=-1)        # Amp LEDs
    amp_variation = GObject.Property(type=bool, default=False)
    am_type   = GObject.Property(type=int, default=0)        # Real Model Code
    am_type_idx   = GObject.Property(type=int, default=-1)        # Combo index
    amp_gain_lvl    = GObject.Property(type=int, default=50)
    amp_vol_lvl  = GObject.Property(type=int, default=50)
    amp_unk1_lvl   = GObject.Property(type=float, default=0.0)
    amp_unk2_lvl   = GObject.Property(type=float, default=0.0)

    def __init__(self, device, ctrl):
        super().__init__(device, ctrl, "Amplifier")
        self.switch_model = False

        self.notify_id = self.connect("notify", self.set_from_ui)

    def set_from_msg(self, name, value):
        name = name.replace('-', '_')
        # log.debug(f">>> {name} = {value}, {type(value)}")
        if name == 'am_type':
            svalue = str(MIDIBytes(value))
            num = list(self.map['Types'].values()).index(svalue)
            self.direct_set('am_type_idx', num)
        else:
            self.direct_set(name, value)

    def set_from_ui(self, obj, pspec):
        name = pspec.name
        value = self.get_property(name)
        # log.debug(f"<<< {name} = {value}, {type(value)}")
        name = name.replace('-', '_')
        if isinstance(value, float):
            value = int(value)
        Addr = self.map.get_addr(name)
        if name == 'am_type_idx':
            model_val = list(self.map['Types'].values())[value]
            Addr  = self.map.get_addr("am_type")
            self.ctrl.send(Addr, model_val, True)
        elif name in ["amp_variation", "amp_num"]:
            num = value if name == 'amp_num' else self.amp_num
            var = value if name == 'amp_variation' else self.amp_variation
            index = num if not var else num + 5
            am_type = list(self.map['Types'].values())[index]
            Addr = self.map.get_addr("am_type")
            am_type = MIDIBytes(am_type)
            self.direct_set("am_type", am_type.int)
            if not self.switch_model:
                self.ctrl.send(Addr, am_type, True)
                self.direct_set("am_type_idx", index)
        elif 'lvl' in name:
            self.ctrl.send(Addr, value, True)

    def set_am_type(self):
        am_type = self.device.mry.read(Address("60 00 00 21"))
        self.direct_set("am_type", am_type.int)
        am_type_code = str(MIDIBytes(self.am_type))
        num = list(self.map['Types'].values()).index(am_type_code)
        self.direct_set("am_type_idx", num)

