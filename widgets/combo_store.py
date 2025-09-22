import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

from lib.midi_bytes import Address, MIDIBytes

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

class ComboStore(Gtk.ComboBox):
    # __gtype_name__ = "Combo-Types/Modes"
    def __init__(self, own_ctrl, key, direct_load=False):
        super().__init__()
        self.own_ctrl = own_ctrl
        lower = own_ctrl.name.lower()
        signal = ''.join(lower.split()) + "-map-ready"
        abrv = lower[:2]+'_' if len(lower.split())==1 \
                else ''.join(v[:1] for v in lower.split())+'_'
        self.key = key
        prop = abrv + key.lower()[:-1] + '_idx'
        self.dest = abrv + key.lower()[:-1]
        log.debug(f"{signal} {abrv=} {self.key} {prop} {self.dest}")

        self.store = Gtk.ListStore(int, str, str)
        self.set_model(self.store)
        renderer = Gtk.CellRendererText()
        self.pack_start(renderer, True)
        self.add_attribute(renderer, "text", 1)
        own_ctrl.bind_property(
            prop, self, "active",
            GObject.BindingFlags.SYNC_CREATE |
            GObject.BindingFlags.BIDIRECTIONAL)

        if direct_load:
            self.types_load(own_ctrl, own_ctrl.map)
        else:
            own_ctrl.connect(signal, self.types_load)

        own_ctrl.device.mry.connect("mry-loaded", self.load_from_mry)


    def types_load(self, own_ctrl, smap):
        models = smap[self.key]
        for i, (name, code) in enumerate(models.items()):
            self.store.append([i, name, code])

    def load_from_mry(self, mry):
        if not hasattr(self.own_ctrl, self.dest):
            log.debug(f"{self.own_ctrl.name} has not {self.dest}")
            return
        val = self.own_ctrl.get_property(self.dest)
        # log.debug(f"{val=}")
        if isinstance(val, int) and val >= 0:
            sval = str(MIDIBytes(val))
            idx = next((row[0] for row in self.store if row[2] == sval), -1)
            # log.debug(f"{idx=}")
            self.set_active(idx)

