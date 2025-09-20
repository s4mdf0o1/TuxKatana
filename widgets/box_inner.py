import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

from .slider import Slider
from .tabbed_panel import TabbedPanel
from .bank import Bank
from .toggle import Toggle
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

class BoxInner(Gtk.Box):
    def __init__(self, label):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=3)

        self.get_style_context().add_class('inner')
        label=Gtk.Label(label=label)
        label.set_xalign(1.0)
        label.set_margin_end(20)
        self.append(label)

