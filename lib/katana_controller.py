import mido
from time import sleep
from gi.repository import GLib

from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import SingleQuotedScalarString as sq
yaml = YAML(typ="rt")

import re
from collections import UserDict
from threading import Thread
from queue import Queue

from .sysex import SysExML, SysExMessage
import logging
from lib.log_setup import LOGGER_NAME
logger = logging.getLogger(LOGGER_NAME)

DEBUG = True
def debug( txt ):
    if DEBUG:
        print(txt)

class KatanaPort:
    def __init__(self):
        self.has_device = False
        self.is_connected = False
        self.index = 0
        self.name = None

        #GLib.timeout_add_seconds(10, self.check_online)

    def check_online( self ):
        debug("KatanaPort.check_online")
        ports = mido.get_output_names()
        self.has_device = any("katana" in p.lower() for p in ports)
        return True

    def list(self):
        debug("KatanaPort.list")
        midi_ports = mido.get_output_names()
        self.ports = [p for p in midi_ports if 'katana' in p.lower() or 'boss' in p.lower()] or None
        if self.ports:
            print(f"Ports MIDI disponibles: {self.ports}")
            self.has_device = True
            for i, port in enumerate(self.ports):
                print(f"{i}: {port}")
 
    def select( self, port_index ):
        self.index= port_index
        print(f"Sélection du port : {self.ports[port_index]}")
        return self.ports[port_index]

    def connect( self, callback ):
        mido.set_backend('mido.backends.rtmidi')
        try:
            if not self.name:
                self.name = self.ports[self.index]
            self.output = mido.open_output(self.name)
            self.input = mido.open_input(self.name, callback=callback)
            self.output.reset()
            print(f"Connecté au Katana sur: {self.name}")
            self.is_connected = True
        except Exception as e:
            self.is_connected = False
            raise Exception(f"Impossible de se connecter au port {self.name}: {e}")

    def send( self, message):#, callback=None ):
        debug(f"send: {message.hex()}")
        #if callback:
        #    self.listener_callback = callback
        #cks = self.checksum( message )
        self.output.send( message )

    def close( self ):
        if hasattr(self, 'output'):
            self.output.close()
        if hasattr(self, 'input'):
            self.input.close()
        print("Connexions MIDI fermées")

class AmpStatus:
    def __init__(self, addr_start ):
        self.addr = addr_start
        self.data = []
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
 
class KatanaController:
    def __init__(self, parent):
        self.parent = parent
        self.port = KatanaPort()
        with open("params/midi.yaml", "r") as f:
            self.midi= yaml.load(f)
        self.pc = mido.Message('program_change')
        self.cc = mido.Message('control_change')
        self.sysex = mido.Message('sysex')
        self.message = SysExMessage()
        self.listener_callback = None
        self.msg_queue = Queue()
        self.thread_watch = Thread(target=self.queue_watcher, daemon=True).start()

        GLib.timeout_add_seconds(1, self.wait_device)

    def queue_watcher(self):
        while True:
            msg = self.msg_queue.get()
            GLib.idle_add(self.message.decode, msg)

    def wait_device(self):
        debug("KatanaController.wait_device")
        self.port.list()
        if self.port.has_device:
            self.port.connect(self.listener)
            sleep(.1)
            self.scan_devices()
            self.parent.win.ks.presets.get_presets()
            return False
        else:
            return True

    def listener(self, msg):
        #debug(f"listener({msg})")
        logger.debug(msg.hex())
        if msg.type == 'sysex':
            try:
                if self.listener_callback:
                    #debug(self.listener_callback)
                    self.listener_callback(msg)
                else:
                    self.msg_queue.put(msg)
                    print("No callback")
                    self.message.decode(msg)
                #self.listener_callback = None
            except:
                import traceback
                traceback.print_exc()
        else:
            try:
                debug(msg)
            except:
                import traceback
                traceback.print_exc()
        self.listener_callback = None

    def send( self, message, callback=None ):
        #debug(f"send: {message.hex()}")
        logger.debug(f"SEND: {message.hex()}")
        if callback:
            self.listener_callback = callback
        self.port.output.send( message )
        sleep(.05)


    def scan_devices(self):
        debug(f"scan_devices()")
        #self.listener_callback = self.set_device
        self.sysex.data = self.message.addrs['SCAN_REQ']
        self.send(self.sysex, self.set_device)
        #self.listener_callback = self.set_name
        msg = self.message.get( 'GET', 'NAME', [0,0,0,0x10])
        #debug(f"{self.message.addrs.to_str(msg)}")
        self.sysex.data = msg
        self.send(self.sysex, self.set_name)

    def set_device(self, msg):
        debug(f"set_device({msg.hex()})")
        data = list(msg.data)
        to_str = self.message.addrs.to_str
        if data[0:4] == self.message.addrs['SCAN_REP']:
            infos = data[4:]
            man = [infos[0]]
            dev = [0]
            mod = [0,0,0,infos[1]]
            num = [infos[2]]
            self.device = {
                "manufacturer": to_str(man),
                "device": to_str(dev),
                "model": sq(to_str(mod)), # Forced string to write YAML
                "number": to_str(num)
                }
            self.message.header = man + dev + mod
            #debug(f"{self.device=}")
            debug(f"message.header= {to_str(self.message.header)}")

    def set_name( self, msg ):
        data = list(msg.data)
        name=""
        if data[0:6] == self.message.header:
            command = data[6]
            function = data[7:11]
            if command == 0x12 and function[0] == 0x10:
                name = ''.join([chr(v) for v in data[11:27]])
                name = name.strip()
        with open("params/devices.yaml", "r") as f:
            devices = yaml.load(f)
        if not devices:
            devices = {}
        if name:
            devices[name] = self.device
        debug(f"{devices=}")
        with open("params/devices.yaml", "w") as f:
            devices = yaml.dump(devices, f)

        self.parent.win.ks.title.set_label(name)
        
    def get_path_val(self, path):
        m = path.split(':')
        val = self.midi
        for key in m:
            val = val[key]
        return val

    def set_on(self, path):
        val = self.get_path_val(path)
        #debug("on:", val, type(val))
        if path.split(':')[0].lower() == "program_change":
            self.pc.program = val
            self.port.send(self.pc)
        else:
            self.cc.control = val['CC']
            self.cc.value = val['ON']
            self.port.send(self.cc)

    def set_off(self, path):
        val = self.get_path_val(path)
        #debug("off:", val)
        self.cc.control = val['CC']
        self.cc.value = val['OFF']
        self.port.send(self.cc)


if __name__ == "__main__":
    from ast import literal_eval
    katana = KatanaController()
    try:
        katana.send("send", "Amp_type", "Lead")
    except KeyboardInterrupt:
        katana.port.close()


