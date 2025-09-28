from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from lib.midi_bytes import Address, MIDIBytes

from lib.map import Map
from lib.effect import Effect

from ruamel.yaml import YAML
yaml = YAML(typ="rt")


class Compressor(Effect, GObject.GObject):
    __gsignals__ = {
        "compressor-map-ready": (GObject.SIGNAL_RUN_FIRST, None, (object,)),
    }
    co_type_idx     = GObject.Property(type=int, default=0)
    co_type         = GObject.Property(type=str)
    co_sus_lvl      = GObject.Property(type=float, default=0.0)
    co_att_lvl      = GObject.Property(type=float, default=0.0)
    co_tone_lvl      = GObject.Property(type=float, default=0.0)
    co_eff_lvl      = GObject.Property(type=float, default=0.0)
    # co_dmix_lvl     = GObject.Property(type=float, default=0.0)

    def __init__(self, device, parent_prefix=""):
        super().__init__("Compressor", device, parent_prefix)
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
        if 'co_type_idx' in name:
            model_val = list(self.map['Types'].values())[value]
            prop = self.parent_prefix+"co_type"
            Addr = self.search_addr(prop)
            # log.debug(f"{prop=} {Addr}")
            self.ctrl.send(Addr, model_val, True)
        else:
            super().set_from_ui(obj, pspec)


