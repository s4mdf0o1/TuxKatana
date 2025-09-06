
from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log_sysex = logging.getLogger(LOGGER_NAME)
dbg = logging.getLogger("debug")

from ruamel.yaml import YAML
yaml = YAML(typ="rt")
from collections import UserDict

from lib.tools import *
from lib.amplifier import Amplifier
from lib.presets import Preset
from lib.memory import Memory
from lib.map import Map

       
class Device(GObject.GObject):
    name = GObject.Property(type=str, default="SETTINGS")
    presets = GObject.Property(type=Gio.ListStore)
    amplifier = GObject.Property(type=object)
    def __init__(self, ctrl):#, addr_start ):
        super().__init__()
        dbg.debug(self.__class__.__name__)
        self.ctrl = ctrl
        self.fsem = ctrl.fsem
        self.mry = Memory(ctrl.fsem)

        self.presets = Gio.ListStore(item_type=Preset)
        self.amplifier=Amplifier(self, ctrl)

        self.is_loading_params = False

        self.data = []

    def send(self, addr, value):
        msg=self.fsem.get_with_addr('SET', addr, value)
        self.ctrl.sysex.data=msg
        self.ctrl.send(self.ctrl.sysex)

    def get_memory(self):
        dbg.debug("Device.get_memory")
        addr = [0x60,0,0,0]
        size = [0,0,0x0f,0]
        msg = self.fsem.get_with_addr('GET', addr, size)
        self.ctrl.sysex.data = msg
        self.ctrl.send(self.ctrl.sysex)

    def get_name(self):
        #addr = from_str(addrs['NAME'])
        size = [0,0,0,0x10]
        msg = self.fsem.get_from_name( 'GET', 'NAME', size)
        self.ctrl.sysex.data = msg
        self.ctrl.send(self.ctrl.sysex, self.set_name_from_data)
        self.amplifier.emit("amp-types-loaded", \
                self.amplifier.map['Type']['Values'])

    def set_name_from_data(self, msg):
        name = self.fsem.get_str(msg).strip()
        self.set_property("name", name)
        self.ctrl.listener_callback= None
        #self.set_name(name)
        
    def get_presets(self):
        size = [0,0,0,0x10]
        #sysex = self.ctrl.message
        for i in range(1,9):
            addr = from_str(self.fsem.addrs['PRESET_'].replace('X', str(i)))
            dbg.debug(f"ADDR: {to_str(addr)}")
            msg = self.fsem.get_with_addr('GET', addr, size)
            dbg.debug(msg)
            self.ctrl.sysex.data = msg
            self.ctrl.send(self.ctrl.sysex, self.set_preset)
        self.ctrl.listener_callback= None

    def set_preset(self, msg):
        addr, data = self.fsem.get_addr_data(msg)
        num = addr[1]
        name = "PRESET_"+str(num)
        pname = self.fsem.get_str(msg).strip()
        label = pname# get_str(msg).strip()
        dbg.debug(f"set_preset: {pname}")
        #addr = to_str(addr)
        self.presets.append(Preset(name=name, label=label, num=num))


    def on_param_changed(self, name, value):
        dbg.debug(f"Device.{name}={value}")

