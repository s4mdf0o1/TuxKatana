from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from lib.midi_bytes import Address, MIDIBytes
from lib.effect import Effect

from lib.map import Map

class AutoWah(Effect, GObject.GObject):
    __gsignals__ = {
        "autowah-map-ready": (GObject.SIGNAL_RUN_FIRST, None, ()),
    }
    aw_filt_sw      = GObject.Property(type=bool, default=False)
    aw_freq_lvl     = GObject.Property(type=float, default=0.0)
    aw_peak_lvl     = GObject.Property(type=float, default=0.0)
    aw_rate_lvl     = GObject.Property(type=float, default=0.0)
    aw_depth_lvl    = GObject.Property(type=float, default=0.0)
    aw_eff_lvl      = GObject.Property(type=float, default=0.0)
    aw_dmix_lvl     = GObject.Property(type=float, default=0.0)

    def __init__(self, device, parent_prefix=""):
        super().__init__("Auto Wah", device, parent_prefix)
        # self.ctrl = ctrl
        # self.device = device

        # self.notify_id = self.connect("notify", self.set_from_ui)

    def set_from_ui(self, obj, pspec):
        name = pspec.name
        value = self.get_property(name)
        # log.debug(f"{name}={value} {self.prefix=}")
        name = name.replace('-','_')
        # log.debug(f"{self.map}")
        prop = self.parent_prefix+name
        Addr = self.search_addr(prop)
        # log.debug(f">>> [{Addr}]> {prop} {name}={value}")
        if 'aw_type_idx' in name:
            model_val = list(self.map['Types'].values())[value]
            prop = self.parent_prefix+"aw_type"
            Addr = self.search_addr(prop)
            # log.debug(f"{prop=} {Addr}")
            if Addr:
                self.ctrl.send(Addr, model_val, True)
        else:
            super().set_from_ui(obj, pspec)


