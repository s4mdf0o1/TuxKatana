from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)
#log = logging.getLogger("debug")

from .tools import *
import numpy as np

from .map import Map
from contextlib import contextmanager

class Amplifier(GObject.GObject):
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
        self.update_source = None

        self._pending = {}
        self._flush_id = None

        self.notify_id = self.connect("notify", self._on_any_property_changed)
        self.mry_id = device.mry.connect("mry-changed", self.load_from_mry)
        self.set_mry_map()

    #def get_type_index_from_map(self, value):

    def on_param_changed(self, name, value):
        log.debug(f">>> {name}={value}")

        prop_name = name.replace('-', '_')
        if name in ["amp-gain", "amp-volume"]:
            actual = int(self.get_property(name.replace('-','-')))
            if prop_name == "amp_gain":
                #prop_addr = self.map.send[prop]
                log.debug(f"{self.map.send[prop_name]=}")
                mry = self.device.mry.read_from_str("60 00 06 51")
            elif prop_name == "amp_volume":
                 mry = self.device.mry.read_from_str("60 00 06 52")
            log.debug(f"{mry=} {actual=} != {int(value)=} ?")
            if mry != int(value):
                saddr = self.map.send[prop_name]
                addr = from_str(saddr)
                val = [int(value)]
                log.debug(f"sending: {saddr=} {val=}")
                self.device.send(addr, val)
                #self.device.mry.write(addr, val)
        elif name in ["amp-variation", "amp-num"]:
            #if int(value) < 10:
                #val = self.encode_type_variation()
                #num_addr = self.map.recv['amp_num']
#            num_addr = next((k for k, v in self.map.recv.items() \
#                        if v == "amp_num"), None)
#            type_addr = next((k for k, v in self.map.recv.items() \
#                        if v == "amp_type"), None)
#            var_addr = next((k for k, v in self.map.recv.items() \
#                        if v == "amp_variation"), None)
#            num_mry = self.device.mry.read_from_str(num_addr)
#            type_mry = self.device.mry.read_from_str(type_addr)#"60 00 00 21")
#            var_mry = self.device.mry.read_from_str(var_addr)
            num_mry = self.get_mry_from_pname("amp_num")
            var_mry = self.get_mry_from_pname("amp_variation")
            log.debug(f"{num_mry=} {var_mry=}")
            #if name =="amp-num":
            #if num_mry != value :
            if name == "amp-variation":
                num = num_mry
                var = value
            else:
                num = value
                var = var_mry
            index = num if not var else num + 5
            log.debug(f"{index=}")
            code_num = list(self.map['Models']['Codes'].values())[index]
            log.debug(f"{code_num=}")
            addr = from_str(self.map.send["amp_type"])
            if self.amp_type < 10:
                self.device.send(addr, from_str(code_num))
                self.handler_block(self.notify_id)
                self.set_property("amp_type", index)
                self.handler_unblock(self.notify_id)
            #code_mry = self.get_mry_from_pname("amp_code")

            #log.debug(f"amp_code-mry: {to_str(code_mry)=}")

            #addr = from_str(self.map.send["amp_type"])
            #self.device.send(addr, val)

        elif name == "amp-type":
            code_mry = self.get_mry_from_pname("amp_code")
            log.debug(f"{name=}: {value=}")

            value = list(self.map['Models']['Codes'].values())[value]
            log.debug(f"mry: {to_str(code_mry)} != {value=}")
            saddr = self.map.send[prop_name]
            addr = from_str(saddr)
            if value != code_mry:
                self.device.send(addr, from_str(value))
            
        elif name == "amp-code":
            idx =list(self.map['Models']['Codes'].values()).index(to_str(value))
            log.debug(f"{to_str(value)=} -> {idx=}")
            self.handler_block(self.notify_id)
            self.set_property("amp_type", idx)
            self.handler_unblock(self.notify_id)

#    def set_with_source(self, prop, value, source):
#        log.debug(f"set_with_source({prop}, {value}, {source})")
#        self.update_source = source
#        self.set_property(prop, value)

    def set_mry_map(self):
        for addr, prop_name in self.map.recv.items():
            log.debug(f"{addr}: {prop_name}")
            self.device.mry.map[addr] = {
                    "obj": self,
                    "prop": prop_name
                }

    #def get_send_addr( self, pname):


    def get_mry_from_pname(self, pname):
        addr = next((k for k, v in self.map.recv.items() \
                if v == pname), None)
        if addr:
            return self.device.mry.read_from_str(addr)
        return None

    def load_from_mry(self, mry):
        for addr, prop_name in self.map.recv.items():
            value = self.device.mry.read_from_str(addr)
            log.debug(f"{prop_name}: {addr}: {to_str(value)}")
            if isinstance(value, int):
                #if prop_name == "amp_code"
                self.handler_block(self.notify_id)
                if prop_name == "amp_code":
                    values = list(self.map["Models"]["Codes"].values())
                    index = values.index(to_str(value))
                    log.debug(f"set_property({prop_name} index:{index}), {type(index)}")
                    self.set_property("amp_type", index)
                else:
                    log.debug(f"set_property({prop_name}, {int(value)}), {type(value)}")
                    self.set_property(prop_name, value)
                self.handler_unblock(self.notify_id)
            else:
                log.warning(f"Amplifier.{prop_name}: {addr} empty value")

    def encode_type_variation(self):
        t = self.amp_num
        v = self.amp_variation

        off = [0x01, 0x08, 0x0B, 0x18, 0x17]
        on = [0x1C, 0x1D, 0x1E, 0x1F, 0x20]
        value = on[t] if v else off[t]
        return [value]

    def set_param( self, name, value):
        self.set_property(name, value)

    def set_amp_type(self, amp_name, amp_code):
        log.debug(f"set_amp_type({amp_name=}, {amp_code=} )")
        mtype = self.map['Models']
        addr = from_str(mtype['SEND'])
        val = from_str(amp_code)
        msg = self.fsem.get_with_addr('SET', addr, val)
        self.ctrl.sysex.data=msg
        self.ctrl.send(self.device.ctrl.sysex)
        
       
    def _on_any_property_changed(self, obj, pspec):
        #log.debug(f"Amplifier._on_any_property_changed: {obj.__class__.__name__}, {pspec.name=}")
        name = pspec.name
        #log.debug(f"_on_any_property: {name}")
        value = self.get_property(name)
        log.debug(f"{name=}: {value=}")
        self._pending[name] = value
        self._schedule_flush()

    def _schedule_flush(self):
        if self._flush_id is None:
            self._flush_id = GLib.timeout_add(100, self._flush)

    def _flush(self):
        for name, value in self._pending.items():
            self.on_param_changed(name, value)

        self._pending.clear()
        self._flush_id = None
        return False


