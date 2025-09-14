from gi.repository import GLib#, GObject, Gio

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

class AntiFlood:
    def __init__(self, *args, delay_ms=100, **kwargs):
        super().__init__(*args, **kwargs)
        self._pending_value = None
        self._flush_id = None
        self._delay_ms = delay_ms

    def schedule_value(self, value):
        """Appelée quand la valeur change trop vite."""
        self._pending_value = value
        if self._flush_id is None:
            self._flush_id = GLib.timeout_add(self._delay_ms, self._flush)

    def _flush(self):
        if self._pending_value is not None:
            self.emit("delayed-value", self._pending_value)  # on émet un signal custom
            self._pending_value = None
        self._flush_id = None
        return False  # stop le timer
    
#class AntiFlood:
#    def __init__(self, *args, **kwargs):
#        super().__init__(*args, **kwargs)
#        self.pending = {}
#        self.flush_id = None
#        self.notify_id = self.scale.connect("notify::value", self.on_any_property_changed)
#        
#    def on_any_property_changed(self, obj, pspec):
#        name = pspec.name
#        value = obj.get_property(name)
#        #log.debug(f"{obj.name=}: {value=}")
#        self.pending[name] = value
#        self.schedule_flush()
#
#    def schedule_flush(self):
#        if self.flush_id is None:
#            self.flush_id = GLib.timeout_add(300, self.flush)
#
#    def flush(self):
#        for name, value in self.pending.items():
#            #self.on_param_changed(name, value)
#            #self.on_param_changed(name, value)
#            log.debug(f"{name=} {value=}")
#
#        self.pending.clear()
#        self.flush_id = None
#        return False

       
