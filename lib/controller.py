import mido
from gi.repository import GLib, GObject

from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import SingleQuotedScalarString as sq
yaml = YAML(typ="rt")

import re
from time import sleep
from threading import Thread, Event
from queue import Queue, Empty

from .midi_port import KatanaPort
from .device import Device
from .midi_bytes import Address, MIDIBytes
from .sysex import SysEx

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
        self.sysex = SysEx()
        self.addrs = {}
        with open("params/midi.yaml", "r") as f:
            self.midi= yaml.load(f)
        for k, v in self.midi['SysEx'].items():
            if len(v.split()) == 4:
                self.addrs[k] = Address(v)
            else:
                self.addrs[k] = MIDIBytes(v)
        self.device = Device(self)
        self.port = KatanaPort()

        self.pc = mido.Message('program_change')
        self.cc = mido.Message('control_change')
        self.msg_queue = Queue()
        self.pause_queue = True
        self.thread_watch = Thread(target=self.queue_watcher, daemon=True).start()
        GLib.timeout_add_seconds(1, self.wait_device)
    
    def wait_msg(self, timeout=0.5):
        msg = self.msg_queue.get(timeout=timeout)
        self.sysex.recvd(msg.data)
        log.sysex(f"{self.sysex.mido.hex()}")
        return self.sysex

    def queue_watcher(self):
        while True:
            if not self.pause_queue:
                msg = self.msg_queue.get(.1)
                log.sysex(f"{msg.hex()}")
                self.sysex.recvd(msg.data)
                addr, data = self.sysex.addr, self.sysex.data
                # log.debug(f"{addr}: {data}")
                GLib.idle_add(self.device.on_received_msg, addr, data)
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

    def send( self, Addr, data=None, SET=False):
        self.device.set_charging(1, 50)
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
        self.device.set_charging(2, 1000)
        # log.debug(sx_msg)
        self.device.get_name()
        self.device.get_presets()
        self.device.set_edit_mode(True)
        self.device.dump_memory()

