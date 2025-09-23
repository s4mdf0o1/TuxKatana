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

