import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

from widgets.slider import Slider
from widgets.toggle import Toggle
from widgets.box_inner import BoxInner
from widgets.combo_store import ComboStore

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from lib.effect import Effect
from lib.set_mapping import add_properties

@add_properties()
class Tmp(Effect, Gtk.Box):
    tmp_lvl     = GObject.Property(type=int, default=0)
    tmp_sw       = GObject.Property(type=bool, default=False)
    pw_type         = GObject.Property(type=str)
    pw_type_idx     = GObject.Property(type=int, default=0)
    def __init__(self, ctrl, pprefx=""):
        super().__init__(ctrl, self.mapping, pprefx)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(6)
        self.parent_prefix = pprefx
    
        box_ = BoxInner("")
        self.append(box_)

        self._lvl = Slider( "", "normal", self, "_lvl" )
        box_aw.append(self._lvl)

        self.filter_sw = Toggle("Low/Pass Band")
        self.bind_property(
            "tw_filt_sw", self.filter_sw,
            "active", GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )
        box_eff.append(self.filter_sw)


