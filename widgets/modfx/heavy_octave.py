
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

from widgets.slider import Slider
from widgets.box_inner import BoxInner

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from lib.effect import Effect
from lib.set_mapping import add_properties

@add_properties()
class HeavyOctave(Effect, Gtk.Box):
    ho_oct1_lvl     = GObject.Property(type=int, default=0)
    ho_oct2_lvl     = GObject.Property(type=int, default=0)
    ho_dmix_lvl     = GObject.Property(type=int, default=0)

    def __init__(self, ctrl, pprefx=""):
        super().__init__(ctrl, self.mapping, pprefx)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(6)
        self.parent_prefix = pprefx

        box = BoxInner("Heavy Octave")
        self.append(box)

        self.ho_oct1 = Slider( "Octave 1", "normal", self, "ho_oct1_lvl" )
        box.append(self.ho_oct1)

        self.ho_oct2 = Slider( "Octave 2", "normal", self, "ho_oct2_lvl" )
        box.append(self.ho_oct2)

        box = BoxInner("Level")
        self.append(box)

        self.ho_dmix = Slider( "Direct Mix", "normal", self, "ho_dmix_lvl" )
        box.append(self.ho_dmix)

