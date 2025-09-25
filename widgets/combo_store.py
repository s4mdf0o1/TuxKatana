import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

from lib.midi_bytes import Address, MIDIBytes

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

class ComboStore(Gtk.ComboBox):
    def __init__(self, parent, store_list, bind_prop):#,direct_load=False):
        super().__init__()
        self.parent = parent
        # signal = parent.signal_name
        # prefix = parent.prefix
        # self.key = key
        # prop = ""
        # if parent.name in ['Mod', 'Fx']:
            # prop = key.lower()[:-1] + '_idx'
        # else:
            # prop = prefix + key.lower()[:-1] + '_idx'
        # self.dest = prefix + key.lower()[:-1]
        # log.debug(f"{signal} {abrv=} {self.key} {prop} {self.dest}")
        self.store = Gtk.ListStore(int, str, str)
        self.set_model(self.store)
        renderer = Gtk.CellRendererText()
        self.pack_start(renderer, True)
        self.add_attribute(renderer, "text", 1)

        for i, (name, code) in enumerate(store_list.items()):
            self.store.append([i, name, code])

        parent.bind_property(
            bind_prop, self, "active",
            GObject.BindingFlags.SYNC_CREATE |
            GObject.BindingFlags.BIDIRECTIONAL)
        log.debug(f"bind to: {bind_prop}")
        # if direct_load:
            # self.types_load(parent, parent.map)
        # else:
            # parent.connect(signal, self.types_load)
        # parent.ctrl.mry.connect("mry-loaded", self.load_from_mry)

    #def load(self, store_list):
    #    #models = smap[self.key]
    #    for i, (name, code) in enumerate(store_list.items()):
    #        self.store.append([i, name, code])

    #def load_from_mry(self, mry):
    #    if not hasattr(self.parent, self.dest):
    #        log.debug(f"{self.parent.name} has not {self.dest}")
    #        return
    #    val = self.parent.get_property(self.dest)
    #    # log.debug(f"{val=}")
    #    if isinstance(val, int) and val >= 0:
    #        sval = str(MIDIBytes(val))
    #        idx = next((row[0] for row in self.store if row[2] == sval), -1)
    #        # log.debug(f"{idx=}")
    #        self.set_active(idx)

