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
        self.prop_idx = bind_prop.replace('_', '-')
        self.prop = self.prop_idx.replace('-idx','')
        self.list_store = list(store_list.inverse)
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
            if not any(row[1] == name \
                    and row[2] == code for row in self.store):
                self.store.append([i, name, code])

        parent.bind_property(
            self.prop_idx, self, "active",
            GObject.BindingFlags.SYNC_CREATE |
            GObject.BindingFlags.BIDIRECTIONAL)
       
        # log.debug(f"bind to: {bind_prop}")

        # type_idx = bind_prop.replace('_', '-')
        # type_name = type_idx.replace('-idx', '')

        # log.debug(f"\033[33m{type_name=}\033[0m")
        self.type_id = self.parent.connect("notify::" + self.prop,
                           self.on_type_change)
        # self.parent.connect("notify::" + type_idx,
                            # self.on_idx_change)
        # self.connect("changed", self.on_idx_change)

    def on_type_change(self, obj, pspec):
        name = pspec.name
        prop = name.replace('-', '_')
        val = obj.get_property(prop)
        idx = self.list_store.index(val)
        current = self.parent.get_property(self.prop_idx)
        # log.debug(f"\033[32m{prop}={val}({idx}/{current})\033[0m")
        if idx != current:
            self.set_active(idx)
        # if val.int != current:
        # self.parent.direct_set(prop+'_idx', idx)

    # def on_idx_change(self, obj, pspec):
    def on_idx_change(self, combo):#obj, pspec):
        idx = combo.get_active()
        val = list(self.parent.types.inverse)[idx]
        pprop = self.prop.replace('_idx', '')
        current = str(MIDIBytes(self.parent.get_property(pprop)))
        # log.debug(f"\033[35m{pprop}={val} / {current}\033[0m")
        if val != current:
            addr = self.parent.mapping[pprop]
            # self.handler_block(self.type_id)
            self.parent.direct_mry(addr, val)
            # self.handler_unblock(self.type_id)

            # if '_idx' in name:
            #     if 'type' in name:
            #         store = self.types
            #         prop = name.replace('_idx', '')
            #     if self.is_modfx:
            #         prop = self.parent_prefix + prop
            #     val = getattr(self, prop)
            #     model_val = MIDIBytes(list(store.inverse)[value])
            #     addr = self.mapping[prop]
            #     current = self.mry.get_value(addr)
            #     log.debug(f"{name}={value} {model_val=} / {addr=} {prop}={val}/{current}")
            #     if current != value:
            #         self.mry.set_value(addr, value)

            
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

