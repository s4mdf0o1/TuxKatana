
from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from ruamel.yaml import YAML
yaml = YAML(typ="rt")
from collections import UserDict

from .midi_bytes import Address, MIDIBytes
from .preset import Preset, Presets
from .amplifier import Amplifier
from .memory import Memory
from .booster import Booster
from .modfx_lib import ModFx
from .reverb import Reverb
from .delay import Delay
from .midi_bytes import Address, MIDIBytes
from .sysex import SysEx

from time import sleep
import time
from queue import Empty

       
class Device(GObject.GObject):
    __gsignals__ = {
        "channel-changed": (GObject.SIGNAL_RUN_FIRST, None, (int,)),
        "edit-toggled": (GObject.SIGNAL_RUN_FIRST, None, (bool,)),
        "preset-changed": (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        "load-maps": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    name = GObject.Property(type=str, default="SETTINGS")
    edit_mode = GObject.Property(type=bool, default=False)
    presets = GObject.Property(type=Gio.ListStore)
    comm  = GObject.Property(type=int, default=0)
    def __init__(self, ctrl):
        super().__init__()
        self.ctrl = ctrl

        self.mry = Memory( self.ctrl.addrs['MEMORY'])
        self.presets = Gio.ListStore(item_type=Presets)
        self.amplifier=Amplifier( self, ctrl )
        self.booster = Booster( self, ctrl )
        self.mod = ModFx( self, ctrl, "Mod" )
        self.fx = ModFx( self, ctrl, "Fx" )
        self.reverb = Reverb( self, ctrl )
        self.delay = Delay( self, ctrl )
        self.preset = Preset(self)
        self.charging = False
        self._charging_id = None

        self.ctrl.parent.connect("main-ready", self.on_main_ready)

    def on_main_ready(self, main):
        # log.debug(f"{main}")
        self.emit("load-maps")

    def on_received_msg(self, addr, data):
        # log.debug(f"{addr} {data}")
        if len(data) > 63:
            self.set_charging(2, 50)
            self.mry.add_block(addr, data)
        else:
            if addr == Address('60 00 00 00').bytes:
                text = ''.join([chr(v) for v in data])
                log.info(f"{text.strip()}")
                return
            self.set_charging(3, 100)
            self.mry.write(addr, data)
            if str(addr) in self.mry.map:
                obj, prop = self.mry.map[str(addr)]
                if hasattr(obj, "prefix"):
                    log.debug(f"{obj.name} > {obj.prefix}")
                    prop = prop.replace(obj.prefix+'_', '')
                value = None
                if isinstance(getattr(obj, prop), bool):
                    value = data.bool
                else:
                    value = data.int
                log.debug(f"{obj.name}[{str(addr)}]: {prop}={value}")
                obj.set_from_msg(prop, value)

            elif str(addr) == '00 01 00 00':
                log.debug(f"emit channel-changed {data}")
                self.emit("channel-changed", data.int)
            else:
                log.warning(f"Device.receive: [{addr}]>_{data}_ not implemented")

    def set_charging(self, state, timeout):
        #log.debug(f"set charging({state})->{timeout} <-{orig}")
        if self._charging_id:
            GLib.source_remove(self._charging_id)
            self._charging_id = None
        self.charging = True
        self.comm = state
        self._charging_id = GLib.timeout_add(timeout, self._end_charging)

    def _end_charging(self):
        self.charging = False
        self._charging_id = None
        self.comm = 0
        return False
    
    def set_midi_channel(self, data):
        self.ctrl.send(Address('00 01 00 00'), MIDIBytes(data), True)

    def dump_memory(self):
        self.ctrl.pause_queue = True
        log.debug("TODO: yaml datas")
        saddr = self.ctrl.addrs['MEMORY']
        sdata = '00 00 0f 48'
        self.ctrl.send(saddr, sdata)
        msgs = []
        while True:
            try:
                sx_msg = self.ctrl.wait_msg(0.2)
                msgs.append(sx_msg.copy())
            except Empty:
                break
        for msg in msgs:
            addr, data = msg.values()
            self.mry.add_block(addr, data)
        self.ctrl.pause_queue = False
        self.preset_name = self.mry.get_actual_preset()

    def set_edit_mode(self, edit):
        if self.edit_mode == edit:
            return
        log.info(f"Edit Mode: {edit}")
        sdata = '01' if edit else '00'
        saddr = self.ctrl.addrs['EDIT_MODE']
        self.ctrl.send(saddr, sdata, True)
        self.edit_mode = edit

    def get_name(self):
        self.ctrl.pause_queue = True
        saddr = self.ctrl.addrs['DEV_NAME']
        sdata = MIDIBytes('10', 4)
        self.ctrl.send(saddr, sdata)
        self.set_name(self.ctrl.wait_msg())
        self.ctrl.pause_queue = False

    def set_name(self, sx_msg):
        name = sx_msg.to_chars()
        log.info(f"Device name: '{name}'")
        self.set_property("name", name)
        
    def get_presets(self):
        self.ctrl.pause_queue = True
        sdata = '00 00 00 10'
        for i in range(1,9):
            saddr = self.ctrl.addrs['PRESET_'+str(i)]
            self.ctrl.send(saddr, sdata)
            self.set_preset(self.ctrl.wait_msg())
        self.ctrl.pause_queue = False

    def set_preset(self, sx_msg):
        label = sx_msg.to_chars()

        num = sx_msg.addr[1]
        name = "PRESET_"+str(num)
        self.presets.append(Presets(name=name, label=label, num=num))

