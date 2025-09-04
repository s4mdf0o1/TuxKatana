
from gi.repository import GLib, GObject
import logging
from lib.log_setup import LOGGER_NAME
log_sysex = logging.getLogger(LOGGER_NAME)
dbg = logging.getLogger("debug")

class Device(GObject.GObject):
    name = GObject.Property(type=str, default="SETTINGS")
    amp_type = GObject.Property(type=int, default=0)
    amp_gain = GObject.Property(type=float, default=0.0)
    __gsignals__ = {
        "amp-type-changed": (GObject.SignalFlags.RUN_LAST, None, (int,)),
        "amp-gain-changed": (GObject.SignalFlags.RUN_LAST, None, (float,))
    #    "name-updated": (GObject.SIGNAL_RUN_LAST, None, (str,))
    }
    def __init__(self, ctrl, addr_start ):
        super().__init__()
        dbg.debug(self.__class__.__name__)
        self.ctrl = ctrl
        self.addr = addr_start
        self.data = []
        self.connect( "amp-type-changed", self.on_param_change)
        self.connect( "amp-gain-changed", self.on_param_change)

    def set_param( self, name, value):
        self.set_property(name, value)
        self.emit(name.replace('_', '-')+"-changed", value)

    def on_param_change(self, obj, *args):
        #dbg.debug(f"on_param_change: {self.amp_type=}")
        #dbg.debug(f"{pspecs=}")
        dbg.debug(f"Signal received from {obj.name} with args={args}")

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
        #self.name = name
        #self.emit("name-updated")
 
