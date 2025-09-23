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


