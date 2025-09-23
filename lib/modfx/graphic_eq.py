from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from lib.midi_bytes import Address, MIDIBytes
from lib.effect import Effect

from lib.map import Map

class GraphicEq(Effect, GObject.GObject):
    __gsignals__ = {
        "graphiceq-map-ready": (GObject.SIGNAL_RUN_FIRST, None, ()),
    }
    ge_31h_lvl    = GObject.Property(type=float, default=0.0)
    ge_62h_lvl    = GObject.Property(type=float, default=0.0)
    ge_125h_lvl     = GObject.Property(type=float, default=0.0)
    ge_250h_lvl     = GObject.Property(type=float, default=0.0)
    ge_500h_lvl     = GObject.Property(type=float, default=0.0)
    ge_1kh_lvl     = GObject.Property(type=float, default=0.0)
    ge_2kh_lvl     = GObject.Property(type=float, default=0.0)
    ge_4kh_lvl     = GObject.Property(type=float, default=0.0)
    ge_8kh_lvl     = GObject.Property(type=float, default=0.0)
    ge_16kh_lvl     = GObject.Property(type=float, default=0.0)
    ge_lev_lvl      = GObject.Property(type=float, default=0.0)

    def __init__(self, device, parent_prefix=""):
        super().__init__("Graphic EQ", device, parent_prefix)
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
        elif not Addr:
            log.warning(f"{name} not found in device.mry.map")

    def set_from_msg(self, name, value):
        name = name.replace('-', '_')
        # log.debug(f">>> {name} = {value}")
        self.direct_set(name, value)


