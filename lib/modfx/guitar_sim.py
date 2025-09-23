
from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from lib.midi_bytes import Address, MIDIBytes
from lib.map import Map
from lib.effect import Effect

from ruamel.yaml import YAML
yaml = YAML(typ="rt")

class GuitarSim(Effect, GObject.GObject):
    __gsignals__ = {
        "guitarsim-map-ready": (GObject.SIGNAL_RUN_FIRST, None, (object,)),
    }
    gs_type         = GObject.Property(type=int, default=0)
    gs_type_idx     = GObject.Property(type=int, default=0)
    gs_low_lvl      = GObject.Property(type=float, default=0.0)
    gs_high_lvl      = GObject.Property(type=float, default=0.0)
    gs_eff_lvl      = GObject.Property(type=float, default=0.0)
    gs_bod_lvl      = GObject.Property(type=float, default=0.0)

    def __init__(self, device, parent_prefix=""):
        super().__init__("Guitar Sim", device, parent_prefix)
        # self.ctrl = ctrl
        # self.device = device

        self.notify_id = self.connect("notify", self.set_from_ui)

    def set_from_ui(self, obj, pspec):
        name = pspec.name.replace('-','_')

        value = self.get_property(name)
        # log.debug(f"{name}={value} {self.prefix=}")
        name = name.replace('-','_')
        # log.debug(f"{self.map}")
        prop = self.parent_prefix+name
        Addr = self.search_addr(prop)
        # log.debug(f">>> [{Addr}]> {prop} {name}={value}")
        if isinstance(value, float):
            value = int(value)
        if 'gs_type_idx' in name:
            model_val = list(self.map['Types'].values())[value]
            prop = self.parent_prefix+"gs_type"
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


