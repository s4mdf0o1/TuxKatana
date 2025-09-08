import mido
from gi.repository import GLib, GObject

from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import SingleQuotedScalarString as sq
yaml = YAML(typ="rt")

import re
from time import sleep
from threading import Thread
from queue import Queue

from .message import FormatMessage
from .midi_port import KatanaPort
from .device import Device
from .tools import to_str, from_str

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)
#log = logging.getLogger("debug")


class KatanaController(GObject.GObject):
    __gsignals__ = {
        "recvd-sysex": (GObject.SignalFlags.RUN_FIRST, None, (object, object)),
    }
    def __init__(self, parent):
        self.parent = parent
        self.fsem = FormatMessage()
        self.device = Device(self)
        self.port = KatanaPort()
        with open("params/midi.yaml", "r") as f:
            self.midi= yaml.load(f)
        self.pc = mido.Message('program_change')
        self.cc = mido.Message('control_change')
        self.sysex = mido.Message('sysex')
        self.listener_callback = None
        self.msg_queue = Queue()
        self.thread_watch = Thread(target=self.queue_watcher, daemon=True).start()

        GLib.timeout_add_seconds(1, self.wait_device)

    def queue_watcher(self):
        #log.debug("queue watcher")
        while True:
            msg = self.msg_queue.get()
            if not self.listener_callback:
                GLib.idle_add(self.device.mry.received_msg, msg)
            else:
                GLib.idle_add(self.listener_callback, msg)

    def wait_device(self):
        log.debug("waiting...")
        self.port.list()
        if self.port.has_device:
            self.port.connect(self.listener)
            sleep(.1)
            self.scan_devices()
            return False
        else:
            return True

    def listener(self, msg):
        #log.debug("listener())")
        #log.sysex(msg.hex())
        if msg.type == 'sysex':
            self.msg_queue.put(msg)

    def send( self, msg, callback=None ):
        #log.debug(f"send: {message.hex()}")
        log.sysex(f"SEND: {msg.hex()}")
        if callback:
            #print(callback)
            self.listener_callback = callback
        self.port.output.send( msg )
        sleep(.05)


    def scan_devices(self):
        log.debug(f"scan_devices()")
        self.sysex.data = from_str(self.fsem.addrs['SCAN_REQ'])
        self.send(self.sysex, self.set_device)

    def set_device(self, msg):
        #log.debug(f"set_device({msg.hex()})")
        data = list(msg.data)
        #to_str = self.message.addrs.to_str
        if data[0:4] == from_str(self.fsem.addrs['SCAN_REP']):
            infos = data[4:]
            man = [infos[0]]
            dev = [0]
            mod = [0,0,0,infos[1]]
            num = [infos[2]]
            self.device.manufacturer = to_str(man)
            self.device.device = to_str(dev)
            self.device.model = sq(to_str(mod))
            self.device.number = to_str(num)
            self.fsem.header = man + dev + mod
            #log.debug(f"{self.device=}")
            #log.debug(f"message.header= {to_str(self.message.header)}")
        self.device.get_name()
        self.device.get_presets()
        self.device.dump_memory()

    def get_path_val(self, path):
        m = path.split(':')
        val = self.midi
        for key in m:
            val = val[key]
        return val

    def set_on(self, path):
        val = self.get_path_val(path)
        #log.debug("on:", val, type(val))
        if path.split(':')[0].lower() == "program_change":
            self.pc.program = val
            self.port.send(self.pc)
        elif path.split(':')[0].lower() == "control_change":
            self.cc.control = val['CC']
            self.cc.value = val['ON']
            self.port.send(self.cc)
        #elif path.split(':')[0].lower() == "sysex":
        #    self.device.

    def set_off(self, path):
        val = self.get_path_val(path)
        #log.debug("off:", val)
        self.cc.control = val['CC']
        self.cc.value = val['OFF']
        self.port.send(self.cc)


