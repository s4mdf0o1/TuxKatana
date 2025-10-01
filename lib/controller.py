import mido
from gi.repository import GLib, GObject, Gio

from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import SingleQuotedScalarString as sq
yaml = YAML(typ="rt")

import re
from time import sleep
from threading import Thread, Event
from queue import Queue, Empty

from .midi_port import KatanaPort
from .preset import Preset, Presets
# from .device import Device
from .midi_bytes import Address, MIDIBytes
from .sysex import SysEx
from .memory import Memory

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)


class Controller(GObject.GObject):
    __gsignals__ = {
        "recvd-sysex": (GObject.SignalFlags.RUN_FIRST, None, (object, object)),

        "channel-changed": (GObject.SIGNAL_RUN_FIRST, None, (int,)),
        "edit-toggled": (GObject.SIGNAL_RUN_FIRST, None, (bool,)),
        "preset-changed": (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        "load-maps": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "status-changed": (GObject.SignalFlags.RUN_FIRST, None, (object, str)),
        # "switch-effect": (GObject.SignalFlags.RUN_FIRST, None, (str,bool,)),
        "load-maps": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }
    name = GObject.Property(type=str, default="SETTINGS")
    edit_mode = GObject.Property(type=bool, default=False)
    presets = GObject.Property(type=Gio.ListStore)
    comm  = GObject.Property(type=int, default=2)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.sysex = SysEx()
        self.addrs = {}
        with open("params/midi.yaml", "r") as f:
            self.midi= yaml.load(f)
        for k, v in self.midi['SysEx'].items():
            if len(v.split()) == 4:
                self.addrs[k] = Address(v)
            else:
                self.addrs[k] = MIDIBytes(v)
        # self.device = Device(self)
        self.port = KatanaPort()

        self.pc = mido.Message('program_change')
        self.cc = mido.Message('control_change')
        self.msg_queue = Queue()
        self.pause_queue = True
        self.thread_watch = Thread(target=self.queue_watcher, daemon=True).start()
        GLib.timeout_add_seconds(1, self.wait_device)
        ###
        self.mry = Memory( self.addrs['MEMORY'])
        self.presets = Gio.ListStore(item_type=Presets)
        # self.amplifier=Amplifier( self )

        self.preset = Preset( self )
        self.charging = False
        self._charging_id = None

        self.parent.connect("main-ready", self.on_main_ready)
        self.mry_id = self.mry.connect("address-changed", self._on_mry_changed)

    def on_main_ready(self, main):
        # log.debug(f"{main}")
        self.emit("load-maps")

    def _on_mry_changed(self, mry, addr, value):
        # log.debug(f"{addr}: {value}")
        self.send(addr, value, True)

    def on_received_msg(self, addr, data):
        log.debug(f"{self.sysex}")
        # log.debug(f"\033[31m◀◁<\033[0m[\033[33m{addr}\033[0m]◁ _\033[34m{data}\033[0m_")
        if len(data) > 63:
            self.set_charging(2, 500)
            self.mry.add_block(addr, data)
        else:
            if addr == Address('60 00 00 00').bytes:
                text = data.to_chars() #''.join([chr(v) for v in data])
                log.info(f"{text.strip()}")
                return
            elif str(addr) == '00 01 00 00':
                # log.debug(f"emit channel-changed {data}")
                self.emit("channel-changed", data.int)
                return
            self.set_charging(3, 500)
            # self.mry.write(addr, data)
            self.mry.handler_block(self.mry_id)
            self.mry.set_value(addr, data)
            self.mry.handler_unblock(self.mry_id)
            return
            # if str(addr) in self.mry.map:
            #     obj, prop = self.mry.map[str(addr)]
            #     if hasattr(obj, "parent_prefix"):
            #         prop = prop.replace(obj.parent_prefix, '')
            #         log.debug(f"{obj.name} > {prop}")
            #     value = None
            #     if isinstance(getattr(obj, prop), bool):
            #         value = data.bool
            #     else:
            #         value = data.int
            #     log.debug(f"{obj.name}[{str(addr)}]: {prop}={value}")
            #     obj.set_from_msg(prop, value)

            # elif str(addr) == '00 01 00 00':
            #     log.debug(f"emit channel-changed {data}")
            #     self.emit("channel-changed", data.int)
            # else:
            #     log.warning(f"Device.receive: [{addr}]>_{data}_ not implemented")

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
        self.send(Address('00 01 00 00'), MIDIBytes(data), True)

    def dump_memory(self):
        self.pause_queue = True
        log.debug("TODO: yaml datas for presets")
        saddr = self.addrs['MEMORY']
        sdata = '00 00 0f 00'
        self.send(saddr, sdata)
        msgs = []
        while True:
            try:
                sx_msg = self.wait_msg(0.2)
                msgs.append(sx_msg.copy())
            except Empty:
                break
        for msg in msgs:
            addr, data = msg.values()
            self.mry.add_block(addr, data)
        self.pause_queue = False
        self.preset_name = self.mry.get_actual_preset()

    def set_edit_mode(self, edit):
        if self.edit_mode == edit:
            return
        log.info(f"Edit Mode: {edit}")
        sdata = '01' if edit else '00'
        saddr = self.addrs['EDIT_MODE']
        self.send(saddr, sdata, True)
        self.edit_mode = edit

    def get_name(self):
        self.pause_queue = True
        saddr = self.addrs['DEV_NAME']
        sdata = MIDIBytes('10', 4)
        self.send(saddr, sdata)
        self.set_name(self.wait_msg())
        self.pause_queue = False

    def set_name(self, sx_msg):
        name = sx_msg.to_chars()
        log.info(f"Device name: '{name}'")
        self.set_property("name", name)
        
    def get_presets(self):
        self.pause_queue = True
        sdata = '00 00 00 10'
        for i in range(1,9):
            saddr = self.addrs['PRESET_'+str(i)]
            self.send(saddr, sdata)
            self.set_preset(self.wait_msg())
        self.pause_queue = False

    def set_preset(self, sx_msg):
        label = sx_msg.to_chars()

        num = sx_msg.addr[1]
        name = "PRESET_"+str(num)
        self.presets.append(Presets(name=name, label=label, num=num))

    ###
    def wait_msg(self, timeout=0.1):
        msg = self.msg_queue.get(timeout=timeout)
        self.sysex.recvd(msg.data)
        log.sysex(f"{msg.hex()}")
        return self.sysex

    def queue_watcher(self):
        while True:
            # log.debug("wait queue")
            if not self.pause_queue:
                msg = self.msg_queue.get(.1)
                log.sysex(f"{msg.hex()}")
                self.sysex.recvd(msg.data)
                addr, data = self.sysex.addr, self.sysex.data
                # log.debug(f"{addr}: {data}")
                GLib.idle_add(self.on_received_msg, addr, data)
            else:
                sleep(.1)

    def wait_device(self):
        log.info("Waiting for device...")
        self.port.list()
        if self.port.has_device:
            self.port.connect(self.listener)
            sleep(.1)
            self.scan_devices()
            return False
        else:
            self.set_charging(2, 1000)
            return True

    def listener(self, msg):
        if msg.type == 'sysex':
            self.msg_queue.put(msg)

    def send( self, Addr, data=None, SET=False):
        self.set_charging(1, 500)
        if not Addr:
            log.debug("Addr Empty")
        msg = self.sysex.get(Addr, data, SET)
        log.sysex(f"SEND: {msg.hex()}")
        log.debug(self.sysex)
        self.port.output.send( msg )

    def scan_devices(self):
        #log.debug(f"-")
        self.pause_queue = True
        scan_req = self.addrs['SCAN_REQ']
        self.send(scan_req)
        self.set_device(self.wait_msg())
        self.pause_queue = False

    def set_device(self, sx_msg):
        self.set_charging(2, 1000)
        # log.debug(sx_msg)
        self.get_name()
        self.get_presets()
        self.set_edit_mode(True)
        self.dump_memory()

