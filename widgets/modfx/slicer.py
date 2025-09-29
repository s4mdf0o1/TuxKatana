
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

from bidict import bidict

from widgets.slider import Slider
from widgets.box_inner import BoxInner
from widgets.combo_store import ComboStore

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from lib.midi_bytes import MIDIBytes
from lib.effect import Effect
from lib.set_mapping import add_properties

@add_properties()
class Slicer(Effect, Gtk.Box):
    sl_pattern      = GObject.Property(type=str)
    sl_pattern_idx  = GObject.Property(type=int, default=0)
    sl_rate_lvl     = GObject.Property(type=int, default=0)
    sl_trig_lvl     = GObject.Property(type=int, default=0)
    sl_eff_lvl      = GObject.Property(type=int, default=0)
    sl_dmix_lvl     = GObject.Property(type=int, default=0)

    def __init__(self, ctrl, pprefx=""):
        super().__init__(ctrl, self.mapping, pprefx)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(6)
        self.parent_prefix = pprefx

        self.patterns=bidict()
        for i in range (20):
            self.patterns[f"P{i+1}"] = MIDIBytes(i).str
    
        self.pattern_list = ComboStore( self, self.patterns, "sl_pattern_idx")
        self.append(self.pattern_list)

        box = BoxInner("Slicer")
        self.append(box)

        self.sl_rate = Slider( "Rate", "normal", self, "sl_rate_lvl" )
        box.append(self.sl_rate)

        self.sl_trig = Slider( "Trig. Sens", "normal", self, "sl_trig_lvl" )
        box.append(self.sl_trig)

        box = BoxInner("Level")
        self.append(box)

        self.sl_eff = Slider( "Effect", "normal", self, "sl_eff_lvl" )
        box.append(self.sl_eff)

        self.sl_dmix = Slider( "Direct Mix", "normal", self, "sl_dmix_lvl" )
        box.append(self.sl_dmix)

    def on_ui_changed(self, obj, pspec):
        name = pspec.name.replace('-','_')
        if not name in self.mapping and not '_idx' in name:
            return
        value = obj.get_property(name)
        # log.debug(f"{name}={value}")
        current = None
        # log.debug(f"{name}={value}/{current}")
        if name.endswith('_idx') and 'pattern' in name:
            name = name.replace('_idx', '')
            value = list(self.patterns.inverse)[value]
            current = self.get_property(name)
            addr = self.mapping.get(name, None)
            if current != value:
                self.direct_mry(addr, value)
        else:
            super().on_ui_changed(obj, pspec)
