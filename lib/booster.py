from gi.repository import GLib, GObject, Gio
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from .midi_bytes import Address, MIDIBytes

from .map import Map
from .effect import Effect

class Booster(Effect, GObject.GObject):
    __gsignals__ = {
        "booster-map-ready": (GObject.SIGNAL_RUN_FIRST, None, (object,)),
    }
    boost_sw            = GObject.Property(type=bool, default=False)
    bo_type         = GObject.Property(type=int, default=0)
    bo_type_idx           = GObject.Property(type=int, default=0)
    boost_solo_sw       = GObject.Property(type=bool, default=False)
    boost_solo_lvl      = GObject.Property(type=float, default=50.0)
    boost_drive_lvl     = GObject.Property(type=float, default=50.0)
    boost_botm_lvl      = GObject.Property(type=float, default=50.0)
    boost_tone_lvl      = GObject.Property(type=float, default=50.0)
    boost_eff_lvl       = GObject.Property(type=float, default=50.0)
    boost_dmix_lvl      = GObject.Property(type=float, default=50.0)
    boost_bank_sel      = GObject.Property(type=int, default=0)
    boost_bank_G        = GObject.Property(type=int, default=0)
    boost_bank_R        = GObject.Property(type=int, default=0)
    boost_bank_Y        = GObject.Property(type=int, default=0)
    boost_status        = GObject.Property(type=int, default=0)
    boost_vol_lvl       = GObject.Property(type=float, default=50.0)

    def __init__(self, device):
        super().__init__("Booster", device, )
        self.banks=['G', 'R', 'Y']

        self.notify_id = self.connect("notify", self.set_from_ui)

    def set_from_msg(self, name, value):
        name = name.replace('-', '_')
        # log.debug(f">>> {name} = {value}")
        if name == 'bo_type':
            svalue = str(MIDIBytes(value))
            num = list(self.map['Types'].values()).index(svalue)
            self.direct_set('bo_type_idx', num)
        else:
            self.direct_set(name, value)
        
    def set_from_ui(self, obj, pspec):
        name = pspec.name
        value = self.get_property(name)
        # log.debug(f"<<< {name} = {value}")
        name = name.replace('-', '_')
        if isinstance(value, float):
            value = int(value)
        Addr = self.map.get_addr(name)
        if name == 'bo_type_idx':
            model_val = list(self.map['Types'].values())[value]
            Addr  = self.map.get_addr("bo_type")
            self.ctrl.send(Addr, model_val)
        elif 'lvl' in name or name == 'boost_bank_sel':
            self.ctrl.send(Addr, value, True)
        elif 'sw' in name:
            value = 1 if value else 0
            self.ctrl.send(Addr, value, True)

    def set_bank_model(self):
        bank = self.banks[self.boost_status - 1]
        bank_name = "boost_bank_"+bank
        model = self.get_property(bank_name)
        smodel = str(MIDIBytes(model))
        num = list(self.map['Types'].values()).index(smodel)
        self.direct_set("bo_type_idx", num)

