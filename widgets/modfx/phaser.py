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
class Phaser(Effect, Gtk.Box):
    ph_type         = GObject.Property(type=str)
    ph_type_idx     = GObject.Property(type=int, default=0)
    ph_rate_lvl     = GObject.Property(type=int, default=0)
    ph_dept_lvl     = GObject.Property(type=int, default=0)
    ph_man_lvl      = GObject.Property(type=int, default=0)
    ph_reso_lvl     = GObject.Property(type=int, default=0)
    ph_stpr_lvl     = GObject.Property(type=int, default=0)
    ph_eff_lvl      = GObject.Property(type=int, default=0)
    ph_dmix_lvl     = GObject.Property(type=int, default=0)
    def __init__(self, ctrl, pprefx=""):
        super().__init__(ctrl, self.mapping, pprefx)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(6)
        self.parent_prefix = pprefx
    

        self.types_list = ComboStore( self, self.types, "ph_type_idx")
        self.append(self.types_list)

        box_se = BoxInner("Phaser")
        self.append(box_se)

        self.ph_rate = Slider( "Rate", "normal", self, "ph_rate_lvl" )
        box_se.append(self.ph_rate)

        self.ph_dept = Slider( "Depth", "normal", self, "ph_dept_lvl" )
        box_se.append(self.ph_dept)

        self.ph_man = Slider( "Manual", "normal", self, "ph_man_lvl" )
        box_se.append(self.ph_man)

        self.ph_reso = Slider( "Reson.", "normal", self, "ph_reso_lvl" )
        box_se.append(self.ph_reso)

        self.ph_stpr = Slider( "Step Rate", "normal", self, "ph_stpr_lvl" )
        box_se.append(self.ph_stpr)

        box = BoxInner("Level")
        self.append(box)

        self.ph_eff = Slider( "Effect", "normal", self, "ph_eff_lvl" )
        box.append(self.ph_eff)

        self.ph_dmix = Slider( "Direct Mix", "normal", self, "ph_dmix_lvl" )
        box.append(self.ph_dmix)

