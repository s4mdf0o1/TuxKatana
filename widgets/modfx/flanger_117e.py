
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
class Flanger117e(Effect, Gtk.Box):
    f1_manu_lvl     = GObject.Property(type=int, default=0)
    f1_widt_lvl     = GObject.Property(type=int, default=0)
    f1_spee_lvl     = GObject.Property(type=int, default=0)
    f1_regn_lvl     = GObject.Property(type=int, default=0)

    def __init__(self, ctrl, pprefx=""):
        super().__init__(ctrl, self.mapping, pprefx)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(6)
        self.parent_prefix = pprefx

        box = BoxInner("Flanger 117E")
        self.append(box)

        self.f1_manu = Slider( "Manual", "normal", self, "f1_manu_lvl" )
        box.append(self.f1_manu)

        self.f1_widt = Slider( "Width", "normal", self, "f1_widt_lvl" )
        box.append(self.f1_widt)

        self.f1_spee = Slider( "Speed", "normal", self, "f1_spee_lvl" )
        box.append(self.f1_spee)

        self.f1_regn = Slider( "Regeneration", "normal", self, "f1_regn_lvl" )
        box.append(self.f1_regn)

