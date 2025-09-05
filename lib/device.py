
from gi.repository import GLib, GObject
import logging
from lib.log_setup import LOGGER_NAME
log_sysex = logging.getLogger(LOGGER_NAME)
dbg = logging.getLogger("debug")

class Device(GObject.GObject):
    name = GObject.Property(type=str, default="SETTINGS")
    presets = GObject.Property(type=object)
    amp_type = GObject.Property(type=int, default=0)
    amp_gain = GObject.Property(type=float, default=0.0)
    amp_volume = GObject.Property(type=float, default=0.0)
    amp_variation = GObject.Property(type=bool, default=False)

    def __init__(self, ctrl, addr_start ):
        super().__init__()
        dbg.debug(self.__class__.__name__)
        self.ctrl = ctrl
        self.sysex = ctrl.message

        self.presets = {}

        self.addr = addr_start
        self.data = []

        self._pending = {}
        self._flush_id = None
        self.connect("notify", self._on_any_property_changed)

    def got_message(self, msg):
        dbg.debug(f"got_message: {msg.hex()}")
        addr, data =  self.sysex.get_addr_data(msg)

    def get_name(self):
        addr = self.sysex.addrs['NAME']
        size = [0,0,0,0x10]
        msg = self.sysex.get( 'GET', 'NAME', size)
        self.ctrl.sysex.data = msg
        self.ctrl.send(self.ctrl.sysex, self.set_name_from_data)

    def set_name(self, name):
        self.set_property("name", name)

    def set_name_from_data(self, msg):
        name = self.sysex.get_str(msg).strip()
        self.set_name(name)
        
    def get_presets(self):
        size = [0,0,0,0x10]
        for i in range(1,9):
            msg = self.sysex.get('GET', 'PRESET_'+str(i), size)
            self.ctrl.sysex.data = msg
            self.ctrl.send(self.ctrl.sysex, self.set_preset)

            #addr = self.message.addrs['PRESET_'+str(i)]
            #data = [0,0,0,0x10]
            #msg = self.sysex.build('GET', addr, data)
            #self.ctrl.send(msg, self.receive_preset)

    def set_preset(self, msg):
        addr, data = self.sysex.get_addr_data(msg)
        name = self.sysex.get_str(msg).strip()
        self.presets[addr[1]] = {'name': name, 'addr': addr}

        #dbg.debug(f"set_preset: {self.presets=}")


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

    def set_param( self, name, value):
        self.set_property(name, value)
   
 
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
