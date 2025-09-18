
from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from ruamel.yaml import YAML
yaml = YAML(typ="rt")
from collections import UserDict

from .tools import *
from .midi_bytes import Address, MIDIBytes
from .preset import Preset, Presets
from .amplifier import Amplifier
from .memory import Memory
from .booster import Booster
from .reverb import Reverb
from .delay import Delay

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
        self.mry = Memory( self.ctrl.se_msg.addrs['MEMORY'])
        self.presets = Gio.ListStore(item_type=Presets)
        self.amplifier=Amplifier( self, ctrl )
        self.booster = Booster( self, ctrl )
        self.reverb = Reverb( self, ctrl )
        self.delay = Delay( self, ctrl )
        self.preset = Preset(self)
        self.charging = False
        self._charging_id = None
        # self.is_loading_params = False

        self.data = []
        self.ctrl.parent.connect("main-ready", self.on_main_ready)

    def on_main_ready(self, main):
        self.emit("load-maps")

    def send(self, Addr, value):
        log.debug(f"[{Addr}]: {to_str(value)}")
        self.set_charging(1, 50)
        msg=self.ctrl.se_msg.get_with_addr('SET', Addr, value)
        self.ctrl.sysex.data=msg
        self.ctrl.send(self.ctrl.sysex)

    # def on_value_changed(self, saddr, value):
        # log.debug(f"{saddr} {value}")

    def on_received_msg(self, addr, data):
        Addr = Address(addr)
        if len(data) > 63:
            self.set_charging(2, 50)
            self.mry.add_block(Addr, data)
        else:
            if addr == Address('60 00 00 00').bytes:
                text = ''.join([chr(v) for v in data])
                log.info(f"{text.strip}")
                return
            self.set_charging(3, 100)
            self.mry.write(Addr, data)
            log.debug(f"{str(Addr)=}: {to_str(data)}")
            if str(Addr) in self.mry.map:
                obj, prop = self.mry.map[str(Addr)]
                value = None
                if isinstance(getattr(obj, prop), bool):
                    value = bool(data[0])
                else:
                    value = int(data[0])
                obj.set_from_msg(prop, value)
                # log.debug(f"{obj.name}: {prop}={value}")

            elif str(Addr) == '00 01 00 00':
                log.debug(f"emit channel-changed {data}")
                self.emit("channel-changed", data[1])
            else:
                log.warning(f"Memory.received_msg: {Addr=}: not implemented")

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
        self.send(Address('00 01 00 00'), from_str(data))

    def dump_memory(self):
        # self.set_charging(2, 10000, "dump_memory")
        self.ctrl.pause_queue = True
        log.debug("TODO: yaml datas")
        Addr = Address('60 00 00 00')
        size = from_str('00 00 0f 48')
        msg = self.ctrl.se_msg.get_with_addr('GET', Addr, size)
        self.ctrl.sysex.data = msg
        self.ctrl.send(self.ctrl.sysex)
        sleep(.1)
        msgs = []
        while True:
            try:
                msg = self.ctrl.msg_queue.get(timeout=0.2)
                msgs.append(msg)
            except Empty:
                break
        for msg in msgs:
            addr, data = self.ctrl.se_msg.get_addr_data(msg)
            self.mry.add_block(Address(to_str(addr)), data)
        #self.mry.emit("mry-loaded")
        self.ctrl.pause_queue = False
        self.preset_name = self.mry.get_preset_name()
        #self.preset.gen()


    # def set_selected_channel(self):
    #     log.debug("-")

    def set_edit_mode(self, edit):
        if self.edit_mode == edit:
            return
        log.info(f"Edit Mode: {edit}")
        val = [1] if edit else [0]
        self.send(Address('7F 00 00 01'), val)
        #self.emit("edit-toggled", val)
        self.edit_mode = edit

    def get_name(self):
        size = [0,0,0,0x10]
        msg = self.ctrl.se_msg.get_from_name( 'GET', 'NAME', size)
        self.ctrl.sysex.data = msg
        self.ctrl.send(self.ctrl.sysex)
        self.set_name(self.ctrl.wait_msg())

    def set_name(self, msg):
        name = self.ctrl.se_msg.get_str(msg).strip()
        log.info(f"Device name: {name}")
        self.set_property("name", name)
        # log.debug(self.ctrl.listener_callback)
        # self.ctrl.listener_callback= None
        
    def get_presets(self):
        size = [0,0,0,0x10]
        for i in range(1,9):
            addr = self.ctrl.se_msg.addrs['PRESET_'+str(i)]
            log.debug(f"{addr=}")
            Addr = self.ctrl.se_msg.addrs['PRESET_'+str(i)]
                           #.replace('X', str(i)))
            msg = self.ctrl.se_msg.get_with_addr('GET', Addr, size)
            self.ctrl.sysex.data = msg
            self.ctrl.send(self.ctrl.sysex)
            self.set_preset(self.ctrl.wait_msg())

    def set_preset(self, msg):
        addr, data = self.ctrl.se_msg.get_addr_data(msg)
        num = addr[1]
        name = "PRESET_"+str(num)
        pname = self.ctrl.se_msg.get_str(msg).strip()
        label = pname
        self.presets.append(Presets(name=name, label=label, num=num))
        # self.ctrl.listener_callback = None

