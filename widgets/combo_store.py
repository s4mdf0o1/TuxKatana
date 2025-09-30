import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

from lib.midi_bytes import Address, MIDIBytes

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

class ComboStore(Gtk.ComboBox):
    def __init__(self, parent, store_list, bind_prop):
        super().__init__()
        self.parent = parent
        self.prop_idx = bind_prop.replace('_', '-')
        self.prop = self.prop_idx.replace('-idx','')
        self.list_store = list(store_list.inverse)
        self.store = Gtk.ListStore(int, str, str)
        self.set_model(self.store)
        renderer = Gtk.CellRendererText()
        self.pack_start(renderer, True)
        self.add_attribute(renderer, "text", 1)

        for i, (name, code) in enumerate(store_list.items()):
            if not any(row[1] == name \
                    and row[2] == code for row in self.store):
                self.store.append([i, name, code])

        parent.bind_property(
            self.prop_idx, self, "active",
            GObject.BindingFlags.SYNC_CREATE |
            GObject.BindingFlags.BIDIRECTIONAL)
       
        self.type_id = self.parent.connect("notify::" + self.prop,
                           self.on_type_change)
    def on_type_change(self, obj, pspec):
        name = pspec.name
        prop = name.replace('-', '_')
        val = obj.get_property(prop)
        idx = self.list_store.index(val)
        current = self.parent.get_property(self.prop_idx)
        if idx != current:
            self.set_active(idx)

    def on_idx_change(self, combo):
        idx = combo.get_active()
        val = list(self.parent.types.inverse)[idx]
        pprop = self.prop.replace('_idx', '')
        current = str(MIDIBytes(self.parent.get_property(pprop)))
        if val != current:
            addr = self.parent.mapping[pprop]
            self.parent.direct_mry(addr, val)

