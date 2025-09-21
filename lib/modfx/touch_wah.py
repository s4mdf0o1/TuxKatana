from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from lib.midi_bytes import Address, MIDIBytes

from lib.map import Map

class TouchWah(GObject.GObject):
    __gsignals__ = {
        "touchwah-map-ready": (GObject.SIGNAL_RUN_FIRST, None, ()),
    }
    tw_filt_sw      = GObject.Property(type=bool, default=False)
    tw_polar_sw     = GObject.Property(type=bool, default=False)
    tw_peak_lvl     = GObject.Property(type=float, default=0.0)
    tw_sens_lvl     = GObject.Property(type=float, default=0.0)
    tw_freq_lvl     = GObject.Property(type=float, default=0.0)
    tw_eff_lvl      = GObject.Property(type=float, default=0.0)
    tw_dmix_lvl     = GObject.Property(type=float, default=0.0)

    def __init__(self, device, ctrl):
        super().__init__()
        self.name = "Touch Wah"
        self.ctrl = ctrl
        self.device = device
        self.map = Map("params/modfx/touch_wah.yaml")
        self.set_mry_map()

        self.banks=['G', 'R', 'Y']

        self.mry_id = device.mry.connect("mry-loaded", self.load_from_mry)
        self.notify_id = self.connect("notify", self.set_from_ui)

        self.device.connect("load-maps", self.load_map)

    def load_map(self, ctrl):
        self.emit("touchwah-map-ready")#, self.map['Types'], self.map['Modes'])

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
        if 'lvl' in name:
            # if name == 'pre_delay_lvl':
            #     value = MIDIBytes(value, 2)
            #     self.ctrl.send(Addr, value, True)
            # else:
            self.ctrl.send(Addr, value, True)
        elif 'sw' in name:
            value = 1 if value else 0
            self.ctrl.send(Addr, value, True)

    def direct_set(self, prop, value):
        self.handler_block_by_func(self.set_from_ui)
        self.set_property(prop, value)
        self.handler_unblock_by_func(self.set_from_ui)


    def load_from_mry(self, mry):
        for saddr, prop in self.map.recv.items():
            value = mry.read(Address(saddr))
            # if prop == 'pre_delay_lvl':
            #     value = mry.read(Address(saddr), 2)
            #     self.direct_set(prop, value.int)
            # else:
            #     if value is not None and value.int >= 0:
            self.direct_set(prop, value.int)

    def set_mry_map(self):
        for Addr, prop in self.map.recv.items():
            self.device.mry.map[str(Addr)] = ( self, prop) 


