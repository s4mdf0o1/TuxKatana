
from gi.repository import GLib, GObject
import logging
from lib.log_setup import LOGGER_NAME
log_sysex = logging.getLogger(LOGGER_NAME)
dbg = logging.getLogger("debug")

class Device(GObject.GObject):
    name = GObject.Property(type=str, default="SETTINGS")
    amp_type = GObject.Property(type=int, default=0)
    amp_gain = GObject.Property(type=float, default=0.0)
    amp_volume = GObject.Property(type=float, default=0.0)
    #__gsignals__ = {
    #    "amp-type-changed": (GObject.SignalFlags.RUN_LAST, None, (int,)),
    #    "amp-gain-changed": (GObject.SignalFlags.RUN_LAST, None, (float,))
    #    "name-updated": (GObject.SIGNAL_RUN_LAST, None, (str,))
    #}
    def __init__(self, ctrl, addr_start ):
        super().__init__()
        dbg.debug(self.__class__.__name__)
        self.ctrl = ctrl

        self.addr = addr_start
        self.data = []

        self._pending = {}
        self._flush_id = None
        self.connect("notify", self._on_any_property_changed)

        #self.connect( "amp-type-changed", self.on_param_change)
        #self.connect( "amp-gain-changed", self.on_param_change)
        #addr = [0,0,0,0]
        #params = { 
        #          "name": { "type": str, "addr": addr,},
        #          "amp_type": { "type": int, "addr": addr,},
        #          "amp_gain": { "type": float, "addr": addr, },
        #          }
        
    def set_param( self, name, value):
        self.set_property(name, value)
        #self.on_param_changed(name, value)
        #self.emit(name.replace('_', '-')+"-changed", value)

    #def on_param_change(self, obj, *args):
    def on_param_changed(self, name, value):
        dbg.debug(f"{name}={value}")

    def get_data_by_addr( self, addr ):
        pass
    def get_data_by_offset( sefl, offset ):
        pass
    def base128(addr, offset):
        b = addr[:]
        b[3] += offset
        for i in range(3,0,-1):
            if b[i] > 127:
                carry = b[i] // 128
                b[i] %= 128
                b[i-1] += carry
        return b
    def set_name(self, name):
        self.set_property("name", name)
 
    def _on_any_property_changed(self, obj, pspec):
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
