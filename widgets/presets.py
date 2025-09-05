import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject
from time import sleep

import logging
dbg=logging.getLogger("debug")

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
        factory = Gtk.SignalListItemFactory()
        factory.connect("setup", self.on_setup)
        factory.connect("bind", self.on_bind)

        selection = Gtk.SingleSelection.new(ctrl.device.presets)
        listview = Gtk.ListView.new(selection, factory)
        self.append(listview)

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

