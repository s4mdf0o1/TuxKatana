import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GObject#, GLib, Gdk

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

dots = [ "⚫", "🟢", "🔴", "🟡" ]

class Toggle(Gtk.ToggleButton):
    def __init__(self, label, path=None, status_id=2):
        super().__init__()
        self.name = label
        self.label_on = dots[status_id] + "  " + label
        self.label_off = dots[0] + "  " + label
        self.status_id = status_id
        self.set_label(self.label_off)
        self.bind_property(
            "active",   # propriété du toggle
            self, "label",
            GObject.BindingFlags.SYNC_CREATE,
            transform_to=self._active_to_label,
        )

        self.set_hexpand(True)
        self.set_halign(Gtk.Align.FILL)

        if path:
            self.path = path
            self.midi_type = path.split(':')[0].lower()

    def _active_to_label(self, binding, active: bool):
        return self.label_on if active else self.label_off

    def set_status_id(self, status_id):
        log.debug(f"{self.name}: {status_id=}")
        self.status_id=status_id
        self.label_on = dots[status_id]+ "  " + self.name
        self.set_label(self._active_to_label(self, self.get_active()))
        active = True if status_id else False
        self.set_active(active)

