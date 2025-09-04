import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk#, GLib, Gdk

import logging
dbg=logging.getLogger("debug")
dots = [ "⚫", "🟢", "🔴", "🟡" ]

class Toggle(Gtk.ToggleButton):
    def __init__(self, label, path=None, status_id=2):
        super().__init__()
        self._label_on = dots[status_id] + "  " + label
        self._label_off = dots[0] + "  " + label
        self.status_id = status_id

        self.set_hexpand(True)
        self.set_halign(Gtk.Align.FILL)

        if path:
            self.path = path
            self.midi_type = path.split(':')[0].lower()
            self.connect("notify::active", self.on_active_changed)

    def on_active_changed(self, button, param): #is_active: bool):
        dbg.debug(f"toggle.Toggle.on_active_changed: {param=}")
        is_active = button.get_active()
        self.set_label(self._label_on if is_active else self._label_off)

    def set_status_id(self, status_id):
        self.status_id=status_id
        self._label_on = dots[status_id]+ "  " + label
        self.on_active_changed(self, color)


