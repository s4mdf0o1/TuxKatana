from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from .tools import *
import numpy as np

from .map import Map
from .anti_flood import AntiFlood

class Amplifier(AntiFlood, GObject.GObject):
    __gsignals__ = {
        "amp-types-loaded": (GObject.SIGNAL_RUN_FIRST, None, (object,)),
    }
    amp_num = GObject.Property(type=int, default=-1)
    amp_type = GObject.Property(type=int, default=-1)
    amp_code = GObject.Property(type=int, default=1)
    amp_gain = GObject.Property(type=int, default=50)
    amp_volume = GObject.Property(type=int, default=50)
    amp_variation = GObject.Property(type=bool, default=False)

    def __init__(self, device, ctrl):
        super().__init__()
        self.ctrl = ctrl
        self.fsem = ctrl.fsem
        self.map = Map("params/amplifier.yaml")
        self.device = device

        self.notify_id = self.connect("notify", self._on_any_property_changed)
        self.mry_id = device.mry.connect("mry-changed", self.load_from_mry)
        self.set_mry_map()

    def on_param_changed(self, name, value):
        log.debug(f">>> {name}={value}")
        prop_name = name.replace('-', '_')
        if name in ["amp-gain", "amp-volume"]:
            #actual = int(self.get_property(name.replace('-','-')))
            if prop_name == "amp_gain":
                mry = self.device.mry.read_from_str("60 00 06 51")
            elif prop_name == "amp_volume":
                 mry = self.device.mry.read_from_str("60 00 06 52")
            if mry != int(value):
                saddr = self.map.send[prop_name]
                addr = from_str(saddr)
                val = [int(value)]
                self.device.send(addr, val)
        elif name in ["amp-variation", "amp-num"]:
            num_mry = self.get_mry_from_pname("amp_num")
            var_mry = self.get_mry_from_pname("amp_variation")
            if name == "amp-variation":
                num = num_mry
                var = value
            else:
                num = value
                var = var_mry
            index = num if not var else num + 5
            code_num = list(self.map['Models']['Codes'].values())[index]
            addr = from_str(self.map.send["amp_type"])
            if self.amp_type < 10:
                self.device.send(addr, from_str(code_num))
                self.handler_block(self.notify_id)
                self.set_property("amp_type", index)
                self.handler_unblock(self.notify_id)
        elif name == "amp-type":
            code_mry = self.get_mry_from_pname("amp_code")
            value = list(self.map['Models']['Codes'].values())[value]
            saddr = self.map.send[prop_name]
            addr = from_str(saddr)
            if value != code_mry:
                self.device.send(addr, from_str(value))
        elif name == "amp-code":
            idx =list(self.map['Models']['Codes'].values()).index(to_str(value))
            self.handler_block(self.notify_id)
            self.set_property("amp_type", idx)
            self.handler_unblock(self.notify_id)

    def set_mry_map(self):
        for addr, prop_name in self.map.recv.items():
            #log.debug(f"{addr}: {prop_name}")
            self.device.mry.map[addr] = {
                    "obj": self,
                    "prop": prop_name
                }

    def get_mry_from_pname(self, pname):
        addr = next((k for k, v in self.map.recv.items() \
                if v == pname), None)
        if addr:
            return self.device.mry.read_from_str(addr)
        return None

    def load_from_mry(self, mry):
        for addr, prop_name in self.map.recv.items():
            value = self.device.mry.read_from_str(addr)
            #log.debug(f"{prop_name}: {addr}: {to_str(value)}")
            if isinstance(value, int):
                self.handler_block(self.notify_id)
                if prop_name == "amp_code":
                    values = list(self.map["Models"]["Codes"].values())
                    index = values.index(to_str(value))
                    #log.debug(f"set_property({prop_name} index:{index}), {type(index)}")
                    self.set_property("amp_type", index)
                else:
                    #log.debug(f"set_property({prop_name}, {int(value)}), {type(value)}")
                    self.set_property(prop_name, value)
                self.handler_unblock(self.notify_id)
            else:
                log.warning(f"Amplifier.{prop_name}: {addr} empty value")

#    def set_param( self, name, value):
#        self.set_property(name, value)

    def set_amp_type(self, amp_name, amp_code):
        #log.debug(f"set_amp_type({amp_name=}, {amp_code=} )")
        mtype = self.map['Models']
        addr = from_str(mtype['SEND'])
        val = from_str(amp_code)
        msg = self.fsem.get_with_addr('SET', addr, val)
        self.ctrl.sysex.data=msg
        self.ctrl.send(self.device.ctrl.sysex)
        
       

