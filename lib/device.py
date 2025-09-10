
from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from ruamel.yaml import YAML
yaml = YAML(typ="rt")
from collections import UserDict

from .tools import *
from .presets import Preset
from .amplifier import Amplifier
from .memory import Memory
from .booster import Booster
#from lib.map import Map

       
class Device(GObject.GObject):
    name = GObject.Property(type=str, default="SETTINGS")
    presets = GObject.Property(type=Gio.ListStore)
    amplifier = GObject.Property(type=object)
    def __init__(self, ctrl):
        super().__init__()
        self.ctrl = ctrl
        self.fsem = ctrl.fsem
        self.mry = Memory(ctrl.fsem)

        self.presets = Gio.ListStore(item_type=Preset)
        self.amplifier=Amplifier( self, ctrl )
        self.booster = Booster( self, ctrl )

        self.is_loading_params = False

        self.data = []

    def send(self, addr, value):
        saddr, sval = to_str(addr), to_str(value)
        log.debug(f"[{saddr}]: {sval}")
        msg=self.fsem.get_with_addr('SET', addr, value)
        self.ctrl.sysex.data=msg
        self.ctrl.send(self.ctrl.sysex)

    def dump_memory(self):
        log.debug("TODO: yaml datas")
        addr = [0x60,0,0,0]
        size = [0,0,0x0f,0]
        msg = self.fsem.get_with_addr('GET', addr, size)
        self.ctrl.sysex.data = msg
        self.ctrl.send(self.ctrl.sysex)

    def set_edit_mode(self, edit):
        log.debug(f"({edit})")
        val = [1] if edit else [0]
        self.send([0x7F,0,0,1], val)

    def get_name(self):
        size = [0,0,0,0x10]
        msg = self.fsem.get_from_name( 'GET', 'NAME', size)
        self.ctrl.sysex.data = msg
        self.ctrl.send(self.ctrl.sysex, self.set_name_from_data)
        self.amplifier.emit("amp-types-loaded", \
                self.amplifier.map['Models'])
        self.booster.emit("booster-loaded", \
                self.booster.map['Models'])

    def set_name_from_data(self, msg):
        name = self.fsem.get_str(msg).strip()
        log.info(f"Device name: {name}")
        self.set_property("name", name)
        self.ctrl.listener_callback= None
        
    def get_presets(self):
        size = [0,0,0,0x10]
        for i in range(1,9):
            addr = from_str(self.fsem.addrs['PRESET_'].replace('X', str(i)))
            msg = self.fsem.get_with_addr('GET', addr, size)
            self.ctrl.sysex.data = msg
            self.ctrl.send(self.ctrl.sysex, self.set_preset)
        self.ctrl.listener_callback= None

    def set_preset(self, msg):
        addr, data = self.fsem.get_addr_data(msg)
        num = addr[1]
        name = "PRESET_"+str(num)
        pname = self.fsem.get_str(msg).strip()
        label = pname
        self.presets.append(Preset(name=name, label=label, num=num))


    def on_param_changed(self, name, value):
        log.debug(f"{name}={value}")

