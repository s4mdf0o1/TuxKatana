from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from lib.midi_bytes import Address, MIDIBytes

from lib.map import Map

class PedalWah(GObject.GObject):
    __gsignals__ = {
        "pedalwah-map-ready": (GObject.SIGNAL_RUN_FIRST, None, (object,)),
    }
    pw_type         = GObject.Property(type=int, default=0)
    pw_type_idx     = GObject.Property(type=int, default=0)
    pw_pos_lvl      = GObject.Property(type=float, default=0.0)
    pw_min_lvl      = GObject.Property(type=float, default=0.0)
    pw_max_lvl      = GObject.Property(type=float, default=0.0)
    pw_eff_lvl      = GObject.Property(type=float, default=0.0)
    pw_dmix_lvl     = GObject.Property(type=float, default=0.0)

    def __init__(self, device, ctrl, parent_prefix=""):
        super().__init__()
        self.name = "Pedal Wah"
        self.ctrl = ctrl
        self.device = device
        self.map = Map("params/modfx/pedal_wah.yaml")
        self.set_mry_map()

        self.banks=['G', 'R', 'Y']

        self.mry_id = device.mry.connect("mry-loaded", self.load_from_mry)
        # self.device.connect("load-maps", self.load_map)
        self.notify_id = self.connect("notify", self.set_from_ui)
        self.load_map(device)


    def load_map(self, device):
        # log.debug(f"{device}")
        self.emit("pedalwah-map-ready", self.map['PWTypes'])#, self.map['Modes'])

    def set_from_msg(self, name, value):
        name = name.replace('-', '_')
        # log.debug(f">>> {name} = {value}")
        self.direct_set(name, value)

    def set_from_ui(self, obj, pspec):
        name = pspec.name
        value = self.get_property(name)
        name = name.replace('-', '_')
        # log.debug(f">>> {name} = {value}")
        if isinstance(value, float):
            value = int(value)
        Addr = self.map.get_addr(name)
        if name == 'type_idx':
            model_val = list(self.map['PWTypes'].values())[value]
            Addr  = self.map.get_addr("pw_type")
            self.ctrl.send(Addr, model_val, True)
        elif 'lvl' in name:
            self.ctrl.send(Addr, value, True)
        elif 'sw' in name:
            value = 1 if value else 0
            self.ctrl.send(Addr, value, True)
        # else:
        #     self.ctrl.send(Addr, value, True)

    def direct_set(self, prop, value):
        self.handler_block_by_func(self.set_from_ui)
        self.set_property(prop, value)
        self.handler_unblock_by_func(self.set_from_ui)

    def load_from_mry(self, mry):
        for saddr, prop in self.map.recv.items():
            value = mry.read(Address(saddr))
            self.direct_set(prop, value.int)

    def set_mry_map(self):
        for Addr, prop in self.map.recv.items():
            self.device.mry.map[str(Addr)] = ( self, prop) 


