from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from .tools import from_str, to_str
import numpy as np

from .map import Map
from .anti_flood import AntiFlood

class Amplifier(AntiFlood, GObject.GObject):
    __gsignals__ = {
        "amp-types-loaded": (GObject.SIGNAL_RUN_FIRST, None, (object,)),
    }
    amp_num     = GObject.Property(type=int, default=-1)            # Base LEDs
    amp_variation = GObject.Property(type=bool, default=False)
    amp_model   = GObject.Property(type=int, default=-1)
    model_idx   = GObject.Property(type=int, default=-1)            # Combo
    gain_lvl    = GObject.Property(type=int, default=50)
    volume_lvl  = GObject.Property(type=int, default=50)
#    amp_code    = GObject.Property(type=int, default=1)

    def __init__(self, device, ctrl):
        super().__init__()
        self.ctrl = ctrl
        self.fsem = ctrl.fsem
        self.map = Map("params/amplifier.yaml")
        self.device = device

        self.notify_id = self.connect("notify", self._on_any_property_changed)
        self.mry_id = device.mry.connect("mry-loaded", self.load_from_mry)
        self.set_mry_map()

    def on_param_changed(self, name, value):
        log.debug(f">>> {name} = {value}")
        name = name.replace('-', '_')
        if not isinstance(value, (int, bool, float)):
            value = from_str(value)
        if isinstance(value, float):
            value = int(value)
        addr = self.map.get_addr(name)
        #mry=None
        #if addr:
        #    mry = self.device.mry.read(addr)
        #log.debug(f"{to_str(addr)}: {value=}, {mry=}")
        if name == 'amp_model':
            num = list(self.map['Models'].values()).index(to_str(value))
            self.direct_set("model_idx", num)
        elif name == 'model_idx':
            model_val = list(self.map['Models'].values())[value]
            addr  = self.map.send["amp_model"]
            self.device.send(from_str(addr), from_str(model_val))
        elif name in ["amp_variation", "amp_num"]:
            num = value if name == 'amp_num' else self.amp_num
            var = value if name == 'amp_variation' else self.amp_variation
            index = num if not var else num + 5
            amp_model = list(self.map['Models'].values())[index]
            addr = from_str(self.map.send["amp_model"])
            if self.model_idx < 10:
                self.device.send(addr, from_str(amp_model))
        elif 'lvl' in name:
            self.device.send(addr, [value])

    def set_mry_map(self):
        for addr, prop in self.map.recv.items():
            #log.debug(f"{addr}: {prop_name}")
            self.device.mry.map[addr] = ( self, prop )

    def direct_set(self, prop, value):
        self.handler_block_by_func(self._on_any_property_changed)
        self.set_property(prop, value)
        self.handler_unblock_by_func(self._on_any_property_changed)

    def load_from_mry(self, mry):
        for addr, prop in self.map.send.inverse.items():
            value = mry.read_from_str(addr)
            #log.debug(f"{prop}: {addr}: {to_str(value)}")
            if value:
                self.direct_set(prop, value)
        for addr, prop in self.map.recv.items():
            value = mry.read_from_str(addr)
            #log.debug(f"{prop}: {addr}: {to_str(value)}")
            if value:
                self.direct_set(prop, value)
        #self.set_bank_model()

 
#    def set_amp_type(self, amp_name, amp_code):
#        #log.debug(f"set_amp_type({amp_name=}, {amp_code=} )")
#        mtype = self.map['Models']
#        addr = from_str(mtype['SEND'])
#        val = from_str(amp_code)
#        msg = self.fsem.get_with_addr('SET', addr, val)
#        self.ctrl.sysex.data=msg
#        self.ctrl.send(self.device.ctrl.sysex)
 
#    def on_param_changed(self, name, value):
#        log.debug(f">>> {name}={value}")
#        prop_name = name.replace('-', '_')
#        if name in ["amp-gain", "amp-volume"]:
#            #actual = int(self.get_property(name.replace('-','-')))
#            if prop_name == "amp_gain":
#                mry = self.device.mry.read_from_str("60 00 06 51")
#            elif prop_name == "amp_volume":
#                 mry = self.device.mry.read_from_str("60 00 06 52")
#            if mry != int(value):
#                saddr = self.map.send[prop_name]
#                addr = from_str(saddr)
#                val = [int(value)]
#                self.device.send(addr, val)
#        elif name in ["amp-variation", "amp-num"]:
#            num_mry = self.get_mry_from_pname("amp_num")
#            var_mry = self.get_mry_from_pname("amp_variation")
#            if name == "amp-variation":
#                num = num_mry
#                var = value
#            else:
#                num = value
#                var = var_mry
#            index = num if not var else num + 5
#            code_num = list(self.map['Models']['Codes'].values())[index]
#            addr = from_str(self.map.send["amp_type"])
#            if self.amp_type < 10:
#                self.device.send(addr, from_str(code_num))
#                self.handler_block(self.notify_id)
#                self.set_property("amp_type", index)
#                self.handler_unblock(self.notify_id)
#        elif name == "amp-type":
#            code_mry = self.get_mry_from_pname("amp_code")
#            value = list(self.map['Models']['Codes'].values())[value]
#            saddr = self.map.send[prop_name]
#            addr = from_str(saddr)
#            if value != code_mry:
#                self.device.send(addr, from_str(value))
#        elif name == "amp-code":
#            idx =list(self.map['Models']['Codes'].values()).index(to_str(value))
#            self.handler_block(self.notify_id)
#            self.set_property("amp_type", idx)
#            self.handler_unblock(self.notify_id)
#    def get_mry_from_pname(self, pname):
#        addr = next((k for k, v in self.map.recv.items() \
#                if v == pname), None)
#        if addr:
#            return self.device.mry.read_from_str(addr)
#        return None


      
       

