from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from lib.midi_bytes import Address, MIDIBytes
from lib.effect import Effect

from lib.map import Map

class Limiter(Effect, GObject.GObject):
    __gsignals__ = {
        "limiter-map-ready": (GObject.SIGNAL_RUN_FIRST, None, ()),
    }
    li_type         = GObject.Property(type=int, default=0)
    li_type_idx     = GObject.Property(type=int, default=0)
    li_attak_lvl    = GObject.Property(type=float, default=0.0)
    li_thold_lvl    = GObject.Property(type=float, default=0.0)
    li_rate_lvl     = GObject.Property(type=float, default=0.0)
    li_rels_lvl     = GObject.Property(type=float, default=0.0)
    li_eff_lvl      = GObject.Property(type=float, default=0.0)
    # li_dmix_lvl     = GObject.Property(type=float, default=0.0)

    def __init__(self, device, parent_prefix=""):
        super().__init__("Limiter", device, parent_prefix)
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
        if 'li_type_idx' in name:
            model_val = list(self.map['Types'].values())[value]
            prop = self.parent_prefix+"li_type"
            Addr = self.search_addr(prop)
            # log.debug(f"{prop=} {Addr}")
            if Addr:
                self.ctrl.send(Addr, model_val, True)
        elif 'lvl' in name:
            if Addr:
                self.ctrl.send(Addr, value, True)
        elif not Addr:
            log.warning(f"{name} not found in device.mry.map")

    def set_from_msg(self, name, value):
        name = name.replace('-', '_')
        # log.debug(f">>> {name} = {value}")
        self.direct_set(name, value)


