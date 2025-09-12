from gi.repository import GLib, GObject, Gio

from lib.tools import to_str, from_str, midi_str_to_int, int_to_midi_bytes

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

class Memory(GObject.GObject):
    __gsignals__ = {
        "mry-loaded": (GObject.SignalFlags.RUN_FIRST, None, ()),
        #"channel-changed": (GObject.SIGNAL_RUN_FIRST, None, (int,)),
    }

    def __init__(self, ctrl):#device, sysex):
        super().__init__()
        self.ctrl = ctrl
        self.sysex = ctrl.fsem #sysex
        self.memory = []
        self.loading = False
        self.base_addr = None
        self.map = {}

    def add_block(self, addr_start, data):
        if addr_start == from_str(self.sysex.addrs['MEMORY']):
            self.loading = True
            self.memory = []
            self.base_addr = addr_start[:]

        if not self.memory:
            self.base_addr = addr_start[:]
            self.memory.extend(data)
            return
        expected_next = self.incr_base128(self.base_addr, len(self.memory))
        if addr_start != expected_next:
            #log.debug("mry-changed")
            self.emit("mry-loaded")
            self.loading = False
            expn = to_str(expected_next)
            adst = to_str(addr_start)
        else:
            self.memory.extend(data)

    def read_from_str(self, saddr, size=1):
        return self.read(from_str(saddr), size)
    def read(self, addr, size=1):
        if not self.base_addr:
            raise RuntimeError("Empty Memory")
        offset = self.addr_to_offset(addr)
        value = self.memory[offset:offset+size]
        if len(value)==size and size==1:
            return value[0]
        else:
            return midi_str_to_int(to_str(value))

    def write_from_str(self, saddr, data):
        self.write( from_str(saddr), data)
    def write(self, addr, data):
        if not self.base_addr:
            raise RuntimeError("Empty Memory")
        offset = self.addr_to_offset(addr)
        if isinstance(data, int):
            data = [data]
        if offset + len(data) > len(self.memory):
            raise IndexError("Write exceeds memory size")
        self.memory[offset:offset + len(data)] = data

    def get_preset_name(self):
        mry_bytes=self.read_from_str('60 00 00 00', 16)
        preset_bytes = int_to_midi_bytes(mry_bytes, 16)
        #log.debug(f"{preset_bytes=}")
        preset_name= ''.join([chr(v) for v in preset_bytes])
        return preset_name


    def received_msg(self, msg):
        log.sysex(f"{msg.hex()}")
        addr, data =  self.sysex.get_addr_data(msg)
        if len(data) > 63:
            self.add_block(addr, data)
        else:
            #self.write(addr, data)
            saddr = to_str(addr)
            sdata = to_str(data)
            #self.emit("mry-changed", saddr)
            #log.debug(f"{saddr=}: {sdata=}")
            if saddr in self.map:
                obj, prop = self.map[saddr]
                #obj = mapping["obj"]
                #prop = mapping["prop"]
                value = None
                if isinstance(getattr(obj, prop), bool):
                    value = bool(data[0])
                else:
                    value = int(data[0])
                setattr(obj, prop, value)
                if saddr in obj.map.recv:
                    self.write(addr, data)
                log.debug(f"{saddr=}: {sdata=}\n\
                    {obj.name}: {prop}={value}")

            elif saddr == '00 01 00 00':
                log.debug(f"emit channel-changed {data}")
                self.ctrl.device.emit("channel-changed", data[1])
            else:
                log.warning(f"Memory.received_msg: {saddr=}: not implemented")
            #self.ctrl.recv_event.set()

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

    def incr_base128(self, addr, n=1):
        b = addr[:]
        for _ in range(n):
            for i in range(len(b)-1, -1, -1):
                b[i] += 1
                if b[i] < 128:
                    break
                b[i] = 0
        return b


