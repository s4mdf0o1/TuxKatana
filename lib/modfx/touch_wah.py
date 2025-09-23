from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from lib.midi_bytes import Address, MIDIBytes

from lib.map import Map
from lib.effect import Effect

class TouchWah(Effect, GObject.GObject):
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

    def __init__(self, device, parent_prefix=""):
        super().__init__("Touch Wah", device, parent_prefix)
        # self.ctrl = ctrl
        # self.device = device

        self.notify_id = self.connect("notify", self.set_from_ui)

    def set_from_ui(self, obj, pspec):
        name = pspec.name
        value = self.get_property(name)
        # log.debug(f"{name}={value} {self.prefix=}")
        name = name.replace('-','_')
        # log.debug(f"{self.map}")
        prop = self.parent_prefix+name
        Addr = self.search_addr(prop)
        # log.debug(f">>> [{Addr}]> {prop} {name}={value}")
        if isinstance(value, float):
            value = int(value)
        if 'lvl' in name:
            if Addr:
                self.ctrl.send(Addr, value, True)
        elif 'sw' in name:
            value = 1 if value else 0
            self.ctrl.send(Addr, value, True)
        elif not Addr:
            log.warning(f"{name} not found in device.mry.map")
           
    def set_from_msg(self, name, value):
        name = name.replace('-', '_')
        # log.debug(f">>> {name} = {value}")
        self.direct_set(name, value)


