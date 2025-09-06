from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log_sysex = logging.getLogger(LOGGER_NAME)
dbg = logging.getLogger("debug")

from .tools import *
import numpy as np

from .map import Map

class Amplifier(GObject.GObject):
    __gsignals__ = {
        "amp-types-loaded": (GObject.SIGNAL_RUN_FIRST, None, (object,)),
    }
    amp_type = GObject.Property(type=str, default="")
    amp_num = GObject.Property(type=int, default=-1)
    amp_gain = GObject.Property(type=float, default=50.0)
    amp_volume = GObject.Property(type=float, default=50.0)
    amp_variation = GObject.Property(type=bool, default=False)
    def __init__(self, device, ctrl):
        super().__init__()
        self.ctrl = ctrl
        self.fsem = ctrl.fsem
        self.map = Map("params/amplifier.yaml")
        self.device = device
        self._pending = {}
        self._flush_id = None
        self.handler_id = self.connect("notify", self._on_any_property_changed)
        self.mry_id = device.mry.connect("mry-changed", self.load_from_mry)
        self.set_mry_map()

    def set_mry_map(self):
        for addr, prop_name in self.map.recv:
            dbg.debug(f"set_mry_map: {addr}: {prop_name}")
            self.device.mry.map[addr] = {
                    "obj": self,
                    "prop": prop_name
                }

    def load_from_mry(self, mry):
        dbg.debug(f"load_from_mry()")
        for addr, prop_name in self.map.recv:
            value = self.device.mry.read_from_str(addr)
            if value:
                self.set_property(prop_name, value)
            else:
                dbg.warning(f"Amplifier.{prop_name}: {addr} empty value")

    def encode_type_variation(self):
        t = self.amp_num
        v = self.amp_variation

        off = [0x01, 0x08, 0x0B, 0x18, 0x17]
        on = [0x1C, 0x1D, 0x1E, 0x1F, 0x20]
        value = on[t] if v else off[t]
        return [value]

    def on_param_changed(self, name, value):
        dbg.debug(f"Amplifier.on_param_changed: {name}={value}")
        if name in ["amp-variation", "amp-num"]:
            if int(value) < 10:
                dbg.debug("CHANGED")
                val = self.encode_type_variation()
                addr = from_str(self.map.send["amp_type"])
                self.device.send(addr, val)
        elif name == "amp-gain":
            addr = from_str(self.map.send["amp_gain"])
            val = [int(value)]
            dbg.debug(val)
            self.device.send(addr, val)
        elif name == "amp-volume":
            addr = from_str(self.map.send["amp_volume"])
            val = [np.int16(value)]
            self.device.send(addr, val)

    def set_param( self, name, value):
        self.set_property(name, value)

    def set_amp_type(self, amp_name, amp_code):
        dbg.debug(f"set_amp_type({amp_name=}, {amp_code=} )")
        mtype = self.map['Type']
        addr = from_str(mtype['SEND'])
        val = from_str(amp_code)
        msg = self.fsem.get_with_addr('SET', addr, val)
        self.ctrl.sysex.data=msg
        self.ctrl.send(self.device.ctrl.sysex)
        
       
    def _on_any_property_changed(self, obj, pspec):
        #dbg.debug(f"Amplifier._on_any_property_changed: {obj.__class__.__name__}, {pspec.name=}")
        name = pspec.name
        value = self.get_property(name)
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


