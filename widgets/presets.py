import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from .preset import PresetUI

class PresetEntry(Gtk.Entry):
    def __init__(self, text):
        super().__init__()
        self.name = text
        self.set_text(text)

class PresetRow(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.num = Gtk.Label(xalign=1)
        self.label = Gtk.Label()
        self.append(self.num)
        self.append(self.label)

class PresetsView(Gtk.Box):

    def __init__(self, ctrl):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.ctrl = ctrl
        self.own_ctrl = self.ctrl.device.presets

        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self.on_setup)
        factory.connect("bind", self.on_bind)

        self.selection = Gtk.SingleSelection.new(ctrl.device.presets)
        listview = Gtk.ListView.new(self.selection, factory)
        self.append(listview)

        self.preset = PresetUI(ctrl.device.preset)
        self.append(self.preset)

        self.selection.connect("selection-changed", self.on_selection_changed)
        self.ctrl.device.mry.connect('mry-loaded', self.on_mry_loaded)


    def on_mry_loaded(self, mry):
        preset_name = self.ctrl.device.mry.get_actual_preset()
        index = self.find_index_by_text(self.selection, preset_name)
        log.debug(f"index={index}, index+1={index+1}")
        self.ctrl.device.emit("channel-changed", int(index+1))

    def on_selection_changed(self, selection, position, n_items):
        index = selection.get_selected()
        if index != Gtk.INVALID_LIST_POSITION:
            item = selection.get_model().get_item(index)
            log.debug(f"Sélectionné index={index}, valeur={item}")
            self.ctrl.device.emit("channel-changed", index+1)

    def find_index_by_text(self, selection, text_to_find):
        model = selection.get_model()
        for i in range(model.get_n_items()):
            preset=model.get_item(i)
            #log.debug(f"{preset.label=} {text_to_find.strip()=}")
            if text_to_find.strip() in preset.label.strip():
                if i>8:
                    log.warning(f"bad index : {i}")
                    return 0
                return i
        return 0 #Gtk.INVALID_LIST_POSITION

    def on_setup(self, factory, list_item):
        row = PresetRow()
        list_item.set_child(row)

    def on_bind(self, factory, list_item):
        row: PresetRow = list_item.get_child()
        preset: Preset = list_item.get_item()

        preset.bind_property(
            "num",
            row.num,
            "label",
            GObject.BindingFlags.SYNC_CREATE,
            transform_to=lambda _b, n: f"CH_{n}:",
        )

        preset.bind_property(
            "label",
            row.label,
            "label",
            GObject.BindingFlags.SYNC_CREATE
        )

