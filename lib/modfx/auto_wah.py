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

    def __init__(self, device, ctrl, parent_prefix=""):
        super().__init__(device, ctrl, "Auto Wah", True, parent_prefix)
        self.ctrl = ctrl
        self.device = device

        self.notify_id = self.connect("notify", self.set_from_ui)

    def set_from_ui(self, obj, pspec):
        name = pspec.name
        value = self.get_property(name)
        log.debug(f"{name}={value} {self.prefix=}")
        name = name.replace('-','_')
        # log.debug(f"{self.map}")
        prop = self.parent_prefix+name
        Addr = self.search_addr(prop)
        log.debug(f">>> [{Addr}]> {prop} {name}={value}")
        if isinstance(value, float):
            value = int(value)
        if 'aw_type_idx' in name:
            model_val = list(self.map['Types'].values())[value]
            prop = self.parent_prefix+"aw_type"
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


       # super().__init__()
       #  self.name = "Auto Wah"
       #  self.ctrl = ctrl
       #  self.device = device
       #  self.map = Map("params/modfx/auto_wah.yaml")
       #  self.set_mry_map()

       #  self.banks=['G', 'R', 'Y']

       #  self.mry_id = device.mry.connect("mry-loaded", self.load_from_mry)
       #  self.notify_id = self.connect("notify", self.set_from_ui)

       #  self.device.connect("load-maps", self.load_map)

    # def load_map(self, ctrl):
       #  self.emit("autowah-map-ready")#, self.map['Types'], self.map['Modes'])

    # def set_from_msg(self, name, value):
       #  name = name.replace('-', '_')
       #  # log.debug(f">>> {name} = {value}")
       #  self.direct_set(name, value)

    # def set_from_ui(self, obj, pspec):
       #  name = pspec.name
       #  value = self.get_property(name)
       #  name = name.replace('-', '_')
       #  # log.debug(f">>> {name} = {value}")
       #  if isinstance(value, float):
       #      value = int(value)
       #  Addr = self.map.get_addr(name)
       #  if 'lvl' in name:
       #      self.ctrl.send(Addr, value, True)
       #  elif 'sw' in name:
       #      value = 1 if value else 0
       #      self.ctrl.send(Addr, value, True)

    # def direct_set(self, prop, value):
       #  self.handler_block_by_func(self.set_from_ui)
       #  self.set_property(prop, value)
       #  self.handler_unblock_by_func(self.set_from_ui)


    # def load_from_mry(self, mry):
       #  for saddr, prop in self.map.recv.items():
       #      value = mry.read(Address(saddr))
       #      self.direct_set(prop, value.int)

    # def set_mry_map(self):
       #  for Addr, prop in self.map.recv.items():
       #      self.device.mry.map[str(Addr)] = ( self, prop) 


