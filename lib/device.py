
from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from ruamel.yaml import YAML
yaml = YAML(typ="rt")
from collections import UserDict

from .tools import *
from .address import Address
#from .presets import Preset
from .amplifier import Amplifier
from .memory import Memory
from .booster import Booster
from .reverb import Reverb
from .delay import Delay
from .preset import Preset, Presets

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
    #amplifier = GObject.Property(type=object)
    def __init__(self, ctrl):
        super().__init__()
        self.ctrl = ctrl
        #self.se_msg = ctrl.se_msg
        self.mry = Memory( self.ctrl.se_msg.addrs['MEMORY'])

        self.presets = Gio.ListStore(item_type=Presets)
        self.amplifier=Amplifier( self, ctrl )
        self.booster = Booster( self, ctrl )
        self.reverb = Reverb( self, ctrl )
        self.delay = Delay( self, ctrl )
        self.preset = Preset(self)

        self.is_loading_params = False

        self.data = []
        self.ctrl.parent.connect("main-ready", self.on_main_ready)

    def on_main_ready(self, main):
        self.emit("load-maps")

    def send(self, Addr, value):
        #sval = to_str(value)
        log.debug(f"[{Addr}]: {to_str(value)}")
        msg=self.ctrl.se_msg.get_with_addr('SET', Addr, value)
        self.ctrl.sysex.data=msg
        self.ctrl.send(self.ctrl.sysex)

    def on_value_changed(self, saddr, value):
        log.debug(f"{saddr} {value}")

    def on_received_msg(self, addr, data):
        Addr = Address(addr)
        if len(data) > 63:
            self.mry.add_block(Addr, data)
        else:
            self.mry.write(Addr, data)
            #saddr = to_str(addr)
            #sdata = to_str(data)
            log.debug(f"{str(Addr)=}: {to_str(data)=}")
            if str(Addr) in self.mry.map:
                obj, prop = self.mry.map[str(Addr)]
                value = None
                if isinstance(getattr(obj, prop), bool):
                    value = bool(data[0])
                else:
                    value = int(data[0])
                obj.set_from_msg(prop, value)
                #setattr(obj, prop, value)
                #if saddr in obj.map.recv:
                    #self.emit("mry-changed", saddr)
                log.debug(f"{obj.name}: {prop}={value}")

            elif str(Addr) == '00 01 00 00':
                log.debug(f"emit channel-changed {data}")
                self.emit("channel-changed", data[1])
            else:
                log.warning(f"Memory.received_msg: {Addr=}: not implemented")
            #self.ctrl.recv_event.set()

    def set_midi_channel(self, data):
        self.send(Address('00 01 00 00'), from_str(data))

    def dump_memory(self):
        self.ctrl.pause_queue = True
        log.debug("TODO: yaml datas")
        Addr = Address('60 00 00 00')
        size = from_str('00 00 0f 00')
        msg = self.ctrl.se_msg.get_with_addr('GET', Addr, size)
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
            addr, data = self.ctrl.se_msg.get_addr_data(msg)
            # log.debug(f"{to_str(addr)}: {len(data)}")
            self.mry.add_block(Address(to_str(addr)), data)
        self.mry.emit("mry-loaded")
        self.ctrl.pause_queue = False
        self.preset_name = self.mry.get_preset_name()
        self.preset.gen()


    def set_selected_channel(self):
        log.debug("-")

    def set_edit_mode(self, edit):
        # log.debug(f"({edit})")
        log.info("Edit Mode")
        val = [1] if edit else [0]
        self.send(Address('7F 00 00 01'), val)

    def get_name(self):
        size = [0,0,0,0x10]
        msg = self.ctrl.se_msg.get_from_name( 'GET', 'NAME', size)
        self.ctrl.sysex.data = msg
        self.ctrl.send(self.ctrl.sysex)#, self.set_name)
        self.set_name(self.ctrl.wait_msg())

    def set_name(self, msg):
        name = self.ctrl.se_msg.get_str(msg).strip()
        log.info(f"Device name: {name}")
        self.set_property("name", name)
        self.ctrl.listener_callback= None
        #self.ctrl.end_seq("set_name")
        
    def get_presets(self):
        size = [0,0,0,0x10]
        for i in range(1,9):
            #if self.ctrl.recv_event.wait(1):
            Addr = Address(self.ctrl.se_msg.addrs['PRESET_'].replace('X', str(i)))
            msg = self.ctrl.se_msg.get_with_addr('GET', Addr, size)
            self.ctrl.sysex.data = msg
            self.ctrl.send(self.ctrl.sysex)#, self.set_preset)
            self.set_preset(self.ctrl.wait_msg())
        #self.ctrl.listener_callback= None

    def set_preset(self, msg):
        addr, data = self.ctrl.se_msg.get_addr_data(msg)
        num = addr[1]
        name = "PRESET_"+str(num)
        pname = self.ctrl.se_msg.get_str(msg).strip()
        label = pname
        self.presets.append(Presets(name=name, label=label, num=num))
        #self.ctrl.end_seq("preset")
        self.ctrl.listener_callback = None


#    def one_param_changed(self, name, value):
#        log.debug(f"{name}={value}")

