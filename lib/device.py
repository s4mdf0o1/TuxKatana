
from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log_sysex = logging.getLogger(LOGGER_NAME)
dbg = logging.getLogger("debug")

def to_str(d):
    if isinstance(d, list):
        return " ".join(f"{i:02x}" for i in d)
    elif isinstance(d, int):
        return f"{d:02x}"

class MemoryMap:
    def __init__(self):
        self.memory = []
        self.base_addr = None

    def incr_base128(self, addr, n=1):
        b = addr[:]
        for _ in range(n):
            for i in range(len(b)-1, -1, -1):
                b[i] += 1
                if b[i] < 128:
                    break
                b[i] = 0
        return b

    def addr_to_offset(self, addr):
        offset = 0
        mult = 1
        for a, b in zip(reversed(addr), reversed(self.base_addr)):
            offset += (a - b) * mult
            mult *= 128
        return offset

    def offset_to_addr(self, offset):
        b = self.base_addr[:]
        for i in range(len(b)-1, -1, -1):
            b[i] += offset % 128
            carry = b[i] // 128
            b[i] %= 128
            offset //= 128
            if carry and i > 0:
                b[i-1] += carry
        return b

    def add_block(self, addr_start, data):
        dbg.debug(f"{len(data)=}")
        if addr_start == [0x60, 0x00, 0x00, 0x00]:
            self.memory = []
            self.base_addr = addr_start[:]

        if not self.memory:
            self.base_addr = addr_start[:]
            self.memory.extend(data)
            return
        #block_offset = self.addr_to_offset(addr_start)
        expected_next = self.incr_base128(self.base_addr, len(self.memory))
        if addr_start != expected_next:
            expn = to_str(expected_next)
            adst = to_str(addr_start)
            dbg.warn(f"Unintended Block: {expn=}, recvd: {adst=}")
            dbg.warn(f"data skipped : {to_str(data)}")
        else:
            self.memory.extend(data)

        #gap = block_offset - len(self.memory)
        #if gap > 0:
        #    self.memory.extend([0x00] * gap)


    def read(self, addr, size=1):
        if not self.base_addr:
            raise RuntimeError("Empty Memory")
        offset = self.addr_to_offset(addr)
        return self.memory[offset:offset+size]

class Preset(GObject.GObject):
    name = GObject.Property(type=str)
    label = GObject.Property(type=str)
    num = GObject.Property(type=int)

class Amplifier(GObject.GObject):
    amp_name = GObject.Property(type=str, default="")
    amp_num = GObject.Property(type=int, default=-1)
    amp_gain = GObject.Property(type=float, default=50.0)
    amp_volume = GObject.Property(type=float, default=50.0)
    amp_variation = GObject.Property(type=bool, default=False)
    def __init__(self, device):
        super().__init__()
        self.device = device
        self._pending = {}
        self._flush_id = None
        self.handler_id = self.connect("notify", self._on_any_property_changed)

    def encode_type_variation(self):
        t = self.amp_num
        v = self.amp_variation
        off = [0x01, 0x08, 0x0B, 0x18, 0x17]
        on = [0x1C, 0x1D, 0x1E, 0x1F, 0x20]
        value = on[t] if v else off[t]
        return value

    def on_param_changed(self, name, value):
        dbg.debug(f"Amplifier.on_param_changed: {name}={value}")
        if name in ["amp-variation", "amp-num"]:
            val = self.encode_type_variation()
            msg=self.device.sysex.get_with_addr('SET', [0x60,0,0,0x21], [val])
            self.device.ctrl.sysex.data=msg
            self.device.ctrl.send(self.device.ctrl.sysex)
            dbg.debug(f"amp: {to_str(msg)=}")

    def set_param( self, name, value):
        self.set_property(name, value)
       
    def _on_any_property_changed(self, obj, pspec):
        dbg.debug(f"Amplifier._on_any_property_changed: {obj.__class__.__name__}, {pspec.name=}")
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

class Device(GObject.GObject):
    name = GObject.Property(type=str, default="SETTINGS")
    presets = GObject.Property(type=Gio.ListStore)
    amplifier = GObject.Property(type=object)

    def __init__(self, ctrl, addr_start ):
        super().__init__()
        dbg.debug(self.__class__.__name__)
        self.ctrl = ctrl
        self.sysex = ctrl.message

        self.presets = Gio.ListStore(item_type=Preset)
        self.amplifier=Amplifier(self)

        self.addr = addr_start
        self.data = []
        self.mry = MemoryMap()
        self.sysex_map = {
            "60 00 06 50": {  # réception type_num
            "obj": self.amplifier,
            "prop": "amp_num",
            "encode": lambda amp: [("60 00 00 21", \
                    self.encode_type_variation(amp))],
            },
            "60 00 06 5c": {  # réception variation
            "obj": self.amplifier,
            "prop": "amp_variation",
            "encode": lambda amp: [("60 00 00 21", \
                    self.encode_type_variation(amp))],
            },
            "60 00 06 51": {  # réception variation
            "obj": self.amplifier,
            "prop": "amp_gain",
                #"encode": lambda amp: [("60 00 06 51", \
                    #self.on_param_changedion(amp))],
            },
            "60 00 06 52": {  # réception variation
            "obj": self.amplifier,
            "prop": "amp_volume",
                #"encode": lambda amp: [("60 00 06 52", \
                    #self.encode_type_variation(amp))],
            },

        }


        #self._pending = {}
        #self._flush_id = None
        #self.connect("notify", self._on_any_property_changed)
        #self.connect("notify", self.on_param_changed)

    def got_message(self, msg):
        #log_sysex.debug(f"{msg.hex()}")
        addr, data =  self.sysex.get_addr_data(msg)
        #dbg.debug(f"{to_str(addr)=} {to_str(data)=} {len(data)=}")
        if len(data) > 63:
            self.mry.add_block(addr, data)
        else:
            saddr = to_str(addr)
            sdata = to_str(data)
            dbg.debug(f"{saddr=}: {sdata=}")
            if saddr in self.sysex_map:
                mapping = self.sysex_map[saddr]
                obj = mapping["obj"]
                prop = mapping["prop"]

                obj.handler_block(obj.handler_id)
                # décodage simple : adapter selon le type
                if isinstance(getattr(obj, prop), bool):
                    setattr(obj, prop, bool(data[0]))
                else:
                    setattr(obj, prop, int(data[0]))
                obj.handler_unblock(obj.handler_id)

#            if addr[:2] == [0x60,0]:
#                dbg.debug(f"{to_str(addr)}: \
#                        {to_str(data)} / \
#                        {to_str(self.mry.read(addr, len(data)))}")
#            else:
#                dbg.debug(f"{to_str(addr)=} {to_str(data)=} {len(data)=}")


    def get_name(self):
        addr = self.sysex.addrs['NAME']
        size = [0,0,0,0x10]
        msg = self.sysex.get_from_name( 'GET', 'NAME', size)
        self.ctrl.sysex.data = msg
        self.ctrl.send(self.ctrl.sysex, self.set_name_from_data)

    #def set_name(self, name):
    #    self.set_property("name", name)

    def set_name_from_data(self, msg):
        name = self.sysex.get_str(msg).strip()
        self.set_property("name", name)
        #self.set_name(name)
        
    def get_presets(self):
        size = [0,0,0,0x10]
        for i in range(1,9):
            msg = self.sysex.get_from_name('GET', 'PRESET_'+str(i), size)
            self.ctrl.sysex.data = msg
            self.ctrl.send(self.ctrl.sysex, self.set_preset)
        self.ctrl.listener_callback= None

    def set_preset(self, msg):
        addr, data = self.sysex.get_addr_data(msg)
        num = addr[1]
        name = "PRESET_"+str(num)
        label = self.sysex.get_str(msg).strip()
        #addr = to_str(addr)
        self.presets.append(Preset(name=name, label=label, num=num))


    def on_param_changed(self, name, value):
        dbg.debug(f"Device.{name}={value}")
#
#    def get_data_by_addr( self, addr ):
#        pass
#    def get_data_by_offset( sefl, offset ):
#        pass
#
#    def base128(addr, offset):
#        b = addr[:]
#        b[3] += offset
#        for i in range(3,0,-1):
#            if b[i] > 127:
#                carry = b[i] // 128
#                b[i] %= 128
#                b[i-1] += carry
#        return b
#
#    def set_param( self, name, value):
#        self.set_property(name, value)
 
#    def _on_any_property_changed(self, obj, pspec):
#        dbg.debug(f"Device._on_any_property_changed: {obj.__class__.__name__}, {pspec.name=}")
#        name = pspec.name
#        value = self.get_property(name)
#        self._pending[name] = value
#        self._schedule_flush()
#
#    def _schedule_flush(self):
#        if self._flush_id is None:
#            self._flush_id = GLib.timeout_add(100, self._flush)
#
#    def _flush(self):
#        for name, value in self._pending.items():
#            self.on_param_changed(name, value)
#
#        self._pending.clear()
#        self._flush_id = None
#        return False
