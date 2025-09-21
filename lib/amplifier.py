from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from .midi_bytes import Address, MIDIBytes

from .map import Map

class Amplifier(GObject.GObject):
    __gsignals__ = {
        "amp-map-ready": (GObject.SIGNAL_RUN_FIRST, None, (object,)),
    }
    amp_num     = GObject.Property(type=int, default=-1)        # Amp LEDs
    amp_variation = GObject.Property(type=bool, default=False)
    amp_model   = GObject.Property(type=int, default=-1)        # Real Model Code
    model_idx   = GObject.Property(type=int, default=-1)        # Combo index
    amp_gain_lvl    = GObject.Property(type=int, default=50)
    amp_vol_lvl  = GObject.Property(type=int, default=50)

    def __init__(self, device, ctrl):
        super().__init__()
        self.name="Ampli"
        self.ctrl = ctrl
        self.device = device
        self.map = Map("params/amplifier.yaml")
        self.set_mry_map()
        self.switch_model = False

        self.mry_id = device.mry.connect("mry-loaded", self.load_from_mry)
        self.device.connect("load-maps", self.load_map)
        self.notify_id = self.connect("notify", self.set_from_ui)

    def load_map(self, ctrl):
        self.emit("amp-map-ready", self.map['Models'])

    def set_from_msg(self, name, value):
        name = name.replace('-', '_')
        # log.debug(f">>> {name} = {value}, {type(value)}")
        if name == 'amp_model':
            svalue = str(MIDIBytes(value))
            num = list(self.map['Models'].values()).index(svalue)
            self.direct_set('model_idx', num)
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
        if name == 'model_idx':
            model_val = list(self.map['Models'].values())[value]
            Addr  = self.map.get_addr("amp_model")
            self.ctrl.send(Addr, model_val, True)
        elif name in ["amp_variation", "amp_num"]:
            num = value if name == 'amp_num' else self.amp_num
            var = value if name == 'amp_variation' else self.amp_variation
            index = num if not var else num + 5
            amp_model = list(self.map['Models'].values())[index]
            Addr = self.map.get_addr("amp_model")
            amp_model = MIDIBytes(amp_model)
            self.direct_set("amp_model", amp_model.int)
            if not self.switch_model:
                self.ctrl.send(Addr, amp_model, True)
                self.direct_set("model_idx", index)
        elif 'lvl' in name:
            self.ctrl.send(Addr, value, True)

    def set_amp_model(self):
        amp_model = self.device.mry.read(Address("60 00 00 21"))
        self.direct_set("amp_model", amp_model.int)
        amp_model_code = str(MIDIBytes(self.amp_model))
        num = list(self.map['Models'].values()).index(amp_model_code)
        self.direct_set("model_idx", num)
 
    def set_mry_map(self):
        for Addr, prop in self.map.recv.items():
            self.device.mry.map[str(Addr)] = ( self, prop )

    def direct_set(self, prop, value):
        # log.debug(prop)
        self.handler_block_by_func(self.set_from_ui)
        self.set_property(prop, value)
        self.handler_unblock_by_func(self.set_from_ui)

    def load_from_mry(self, mry):
        #log.debug(self.map.recv.items())
        for saddr, prop in self.map.recv.items():
            value = mry.read(Address(saddr))
            # log.debug(f"{saddr} {value.int=}")
            if value is not None and value.int >= 0:
                self.direct_set(prop, value.int)
        self.set_amp_model()

