from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from lib.midi_bytes import Address, MIDIBytes
from lib.effect import Effect

from lib.map import Map

class ParametricEq(Effect, GObject.GObject):
    __gsignals__ = {
        "graphiceq-map-ready": (GObject.SIGNAL_RUN_FIRST, None, ()),
    }
    pe_loco_lvl = GObject.Property(type=float, default=0.0)
    pe_loga_lvl = GObject.Property(type=float, default=0.0)
    pe_lomf_lvl = GObject.Property(type=float, default=0.0)
    pe_lomq_lvl = GObject.Property(type=float, default=0.0)
    pe_lomg_lvl = GObject.Property(type=float, default=0.0)
    pe_himf_lvl = GObject.Property(type=float, default=0.0)
    pe_himq_lvl = GObject.Property(type=float, default=0.0)
    pe_himg_lvl = GObject.Property(type=float, default=0.0)
    pe_higa_lvl = GObject.Property(type=float, default=0.0)
    pe_hico_lvl = GObject.Property(type=float, default=0.0)
    pe_lev_lvl  = GObject.Property(type=float, default=0.0)

    def __init__(self, device, parent_prefix=""):
        super().__init__("Parametric EQ", device, parent_prefix)



