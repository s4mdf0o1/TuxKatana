import mido
from gi.repository import GLib, GObject

from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import SingleQuotedScalarString as sq
yaml = YAML(typ="rt")

import re
from time import sleep
from threading import Thread, Event
from queue import Queue, Empty

from .message import FormatMessage
from .midi_port import KatanaPort
from .device import Device
from .tools import to_str, from_str

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)


class Controller(GObject.GObject):
    __gsignals__ = {
        "recvd-sysex": (GObject.SignalFlags.RUN_FIRST, None, (object, object)),
    }
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.se_msg = FormatMessage()
        self.device = Device(self)
        self.port = KatanaPort()
        with open("params/midi.yaml", "r") as f:
            self.midi= yaml.load(f)
        self.pc = mido.Message('program_change')
        self.cc = mido.Message('control_change')
        self.sysex = mido.Message('sysex')
        # self.listener_callback = None
        self.msg_queue = Queue()
        self.pause_queue = True
        self.thread_watch = Thread(target=self.queue_watcher, daemon=True).start()
        GLib.timeout_add_seconds(1, self.wait_device)
    
    def wait_msg(self):
        return self.msg_queue.get(timeout=0.5)

    def queue_watcher(self):
        while True:
            if not self.pause_queue:
                msg = self.msg_queue.get(.1)
                log.sysex(f"{msg.hex()}")
                addr, data =  self.se_msg.get_addr_data(msg)
                GLib.idle_add(self.device.on_received_msg, addr, data,priority=GLib.PRIORITY_DEFAULT)
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
            return True

    def listener(self, msg):
        if msg.type == 'sysex':
            self.msg_queue.put(msg)

    def send( self, msg):#, callback=None ):
        #self.device.comm=1
        log.sysex(f"SEND: {msg.hex()}")
        # log.debug(msg.hex())
        # if callback:
            # log.debug("has callback")
            # self.listener_callback = callback
        self.port.output.send( msg )

    def scan_devices(self):
        #log.debug(f"-")
        self.sysex.data = self.se_msg.addrs['SCAN_REQ'].bytes
        self.send(self.sysex)
        self.set_device(self.wait_msg())

    def set_device(self, msg):
        #log.debug(msg)
        self.device.set_charging(2, 1000)
        data = list(msg.data)
        if data[0:4] == self.se_msg.addrs['SCAN_REP'].bytes:
            infos = data[4:]
            man = [infos[0]]
            dev = [0]
            mod = [0,0,0,infos[1]]
            num = [infos[2]]
            self.device.manufacturer = to_str(man)
            self.device.device = to_str(dev)
            self.device.model = sq(to_str(mod))
            self.device.number = to_str(num)
            self.se_msg.header = man + dev + mod
        self.device.get_name()
        self.device.get_presets()
        self.device.set_edit_mode(True)
        self.device.dump_memory()
        # self.device.set_selected_channel()

