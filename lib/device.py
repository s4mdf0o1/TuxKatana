
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
from .reverb import Reverb
from .delay import Delay

#from lib.map import Map
from time import sleep
from queue import Empty

       
class Device(GObject.GObject):
    __gsignals__ = {
        "channel-changed": (GObject.SIGNAL_RUN_FIRST, None, (int,)),
        "preset-changed": (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        "load-maps": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    name = GObject.Property(type=str, default="SETTINGS")
    presets = GObject.Property(type=Gio.ListStore)
    amplifier = GObject.Property(type=object)
    def __init__(self, ctrl):
        super().__init__()
        self.ctrl = ctrl
        self.fsem = ctrl.fsem
        self.mry = Memory(ctrl)

        self.presets = Gio.ListStore(item_type=Preset)
        self.amplifier=Amplifier( self, ctrl )
        self.booster = Booster( self, ctrl )
        self.reverb = Reverb( self, ctrl )
        self.delay = Delay( self, ctrl )

        self.is_loading_params = False

        self.data = []
        self.ctrl.parent.connect("main-ready", self.on_main_ready)

    def on_main_ready(self, main):
        self.emit("load-maps")


    def send(self, addr, value):
        saddr, sval = to_str(addr), to_str(value)
        log.debug(f"[{saddr}]: {sval}")
        msg=self.fsem.get_with_addr('SET', addr, value)
        self.ctrl.sysex.data=msg
        self.ctrl.send(self.ctrl.sysex)

    def set_midi_channel(self, data):
        self.send(from_str('00 01 00 00'), from_str(data))

    def dump_memory(self):
        self.ctrl.pause_queue = True
        log.debug("TODO: yaml datas")
        addr = [0x60,0,0,0]
        size = [0,0,0x0f,0]
        msg = self.fsem.get_with_addr('GET', addr, size)
        self.ctrl.sysex.data = msg
        self.ctrl.send(self.ctrl.sysex)
        sleep(.1)
        msgs = []
        while True:
            try:
                msg = self.ctrl.msg_queue.get(timeout=0.5)
                msgs.append(msg)
            except Empty:
                break
        for msg in msgs:
            addr, data = self.ctrl.fsem.get_addr_data(msg)
            log.debug(f"{to_str(addr)}: {len(data)}")
            self.mry.add_block(addr, data)
        self.ctrl.pause_queue = False

    def set_selected_channel(self):
        log.debug("-")

    def set_edit_mode(self, edit):
        #log.debug(f"({edit})")
        log.info("Edit Mode")
        val = [1] if edit else [0]
        self.send([0x7F,0,0,1], val)

    def get_name(self):
        size = [0,0,0,0x10]
        msg = self.fsem.get_from_name( 'GET', 'NAME', size)
        self.ctrl.sysex.data = msg
        self.ctrl.send(self.ctrl.sysex)#, self.set_name)
        self.set_name(self.ctrl.wait_msg())

    def set_name(self, msg):
        name = self.fsem.get_str(msg).strip()
        log.info(f"Device name: {name}")
        self.set_property("name", name)
        self.ctrl.listener_callback= None
        #self.ctrl.end_seq("set_name")
        
    def get_presets(self):
        size = [0,0,0,0x10]
        for i in range(1,9):
            #if self.ctrl.recv_event.wait(1):
            addr = from_str(self.fsem.addrs['PRESET_'].replace('X', str(i)))
            msg = self.fsem.get_with_addr('GET', addr, size)
            self.ctrl.sysex.data = msg
            self.ctrl.send(self.ctrl.sysex)#, self.set_preset)
            self.set_preset(self.ctrl.wait_msg())
        #self.ctrl.listener_callback= None

    def set_preset(self, msg):
        addr, data = self.fsem.get_addr_data(msg)
        num = addr[1]
        name = "PRESET_"+str(num)
        pname = self.fsem.get_str(msg).strip()
        label = pname
        self.presets.append(Preset(name=name, label=label, num=num))
        #self.ctrl.end_seq("preset")
        self.ctrl.listener_callback = None


#    def one_param_changed(self, name, value):
#        log.debug(f"{name}={value}")

