import mido
from gi.repository import GLib, GObject

from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import SingleQuotedScalarString as sq
yaml = YAML(typ="rt")

import re
from time import sleep
from threading import Thread
from queue import Queue

from .sysex import SysExML, SysExMessage
from .midi_port import KatanaPort
from .device import Device

import logging
from lib.log_setup import LOGGER_NAME
log_sysex = logging.getLogger(LOGGER_NAME)
dbg = logging.getLogger("debug")


class KatanaController:
    def __init__(self, parent):
        self.parent = parent
        self.message = SysExMessage()
        self.device = Device(self, [0x60,0,0,0])
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
        while True:
            msg = self.msg_queue.get()
            #GLib.idle_add(self.message.decode, msg)
            dbg.debug(f"{self.listener_callback=}")
            if not self.listener_callback:
                GLib.idle_add(self.device.got_message, msg)
            else:
                GLib.idle_add(self.listener_callback, msg)

    def wait_device(self):
        dbg.debug("KatanaController.wait_device")
        self.port.list()
        if self.port.has_device:
            self.port.connect(self.listener)
            sleep(.1)
            self.scan_devices()

            #self.parent.win.ks.presets.get_presets()
            return False
        else:
            return True

    def listener(self, msg):
        #dbg.debug(f"listener({msg})")
        log_sysex.debug(msg.hex())
        if msg.type == 'sysex':
            self.msg_queue.put(msg)
#            try:
#                if self.listener_callback:
#                    #dbg.debug(self.listener_callback)
#                    self.listener_callback(msg)
#                else:
#                    self.msg_queue.put(msg)
#                    #print("No callback")
#                    #self.message.decode(msg)
#            except:
#                import traceback
#                traceback.print_exc()
#        else:
#            try:
#                dbg.debug(msg)
#            except:
#                import traceback
#                traceback.print_exc()
        #self.listener_callback = None

    def send( self, message, callback=None ):
        #dbg.debug(f"send: {message.hex()}")
        log_sysex.debug(f"SEND: {message.hex()}")
        if callback:
            self.listener_callback = callback
        self.port.output.send( message )
        sleep(.05)


    def scan_devices(self):
        dbg.debug(f"scan_devices()")
        #self.listener_callback = self.set_device
        self.sysex.data = self.message.addrs['SCAN_REQ']
        self.send(self.sysex, self.set_device)
        #self.listener_callback = self.set_name
        #msg = self.message.get( 'GET', 'NAME', [0,0,0,0x10])
        #dbg.debug(f"{self.message.addrs.to_str(msg)}")

    def set_device(self, msg):
        dbg.debug(f"set_device({msg.hex()})")
        data = list(msg.data)
        to_str = self.message.addrs.to_str
        if data[0:4] == self.message.addrs['SCAN_REP']:
            infos = data[4:]
            man = [infos[0]]
            dev = [0]
            mod = [0,0,0,infos[1]]
            num = [infos[2]]
            self.device.manufacturer = to_str(man)
            self.device.device = to_str(dev)
            self.device.model = sq(to_str(mod))
            self.device.number = to_str(num)
            self.message.header = man + dev + mod
            dbg.debug(f"{self.device=}")
            dbg.debug(f"message.header= {to_str(self.message.header)}")
        self.device.get_name()
        self.device.get_presets()

#    def set_name( self, msg ):
#        data = list(msg.data)
#        name=""
#        if data[0:6] == self.message.header:
#            command = data[6]
#            function = data[7:11]
#            if command == 0x12 and function[0] == 0x10:
#                name = ''.join([chr(v) for v in data[11:27]])
#                name = name.strip()
#        with open("params/devices.yaml", "r") as f:
#            devices = yaml.load(f)
#        if not devices:
#            devices = {}
#        if name:
#            devices[name] = {
#                    "manufacturer": self.device.manufacturer,
#                    "device": self.device.device,
#                    "model": self.device.model,
#                    "number": self.device.number
#                    }
#        dbg.debug(f"{devices=}")
#        with open("params/devices.yaml", "w") as f:
#            devices = yaml.dump(devices, f)
#
#        #self.parent.win.ks.title.set_label(name)
#        self.device.set_name(name)
#        self.device.amp_type = 1
        
    def get_path_val(self, path):
        m = path.split(':')
        val = self.midi
        for key in m:
            val = val[key]
        return val

    def set_on(self, path):
        val = self.get_path_val(path)
        #dbg.debug("on:", val, type(val))
        if path.split(':')[0].lower() == "program_change":
            self.pc.program = val
            self.port.send(self.pc)
        else:
            self.cc.control = val['CC']
            self.cc.value = val['ON']
            self.port.send(self.cc)

    def set_off(self, path):
        val = self.get_path_val(path)
        #dbg.debug("off:", val)
        self.cc.control = val['CC']
        self.cc.value = val['OFF']
        self.port.send(self.cc)


