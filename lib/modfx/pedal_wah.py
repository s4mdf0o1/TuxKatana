from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from lib.midi_bytes import Address, MIDIBytes
from lib.effect import Effect

from lib.map import Map

class PedalWah(Effect, GObject.GObject):
    __gsignals__ = {
        "pedalwah-map-ready": (GObject.SIGNAL_RUN_FIRST, None, (object,)),
    }
    pw_type_idx     = GObject.Property(type=int, default=0)
    pw_type         = GObject.Property(type=str)
    pw_pos_lvl      = GObject.Property(type=float, default=0.0)
    pw_min_lvl      = GObject.Property(type=float, default=0.0)
    pw_max_lvl      = GObject.Property(type=float, default=0.0)
    pw_eff_lvl      = GObject.Property(type=float, default=0.0)
    pw_dmix_lvl     = GObject.Property(type=float, default=0.0)

    def __init__(self, device, parent_prefix=""):
        super().__init__("Pedal Wah", device, parent_prefix)
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
        if 'pw_type_idx' in name:
            model_val = list(self.map['Types'].values())[value]
            prop = self.parent_prefix+"pw_type"
            Addr = self.search_addr(prop)
            # log.debug(f"{prop=} {Addr}")
            self.ctrl.send(Addr, model_val, True)
        else:
            super().set_from_ui(obj, pspec)

    # def set_from_msg(self, name, value):
    #     name = name.replace('-', '_')
    #     # log.debug(f">>> {name} = {value}")
    #     self.direct_set(name, value)


