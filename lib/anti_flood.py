from gi.repository import GLib#, GObject, Gio

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

class AntiFlood:
    def __init__(self):
        super().__init__()
        self._pending = {}
        self._flush_id = None
        
    def _on_any_property_changed(self, obj, pspec):
        name = pspec.name
        value = self.get_property(name)
        #log.debug(f"{obj.name=}: {value=}")
        self._pending[name] = value
        self._schedule_flush()

    def _schedule_flush(self):
        if self._flush_id is None:
            self._flush_id = GLib.timeout_add(100, self._flush)

    def _flush(self):
        for name, value in self._pending.items():
            self.on_param_changed(name, value)

        self._pending.clear()
        self._flush_id = None
        return False

       
