
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

from widgets.slider import Slider
from widgets.box_inner import BoxInner
from widgets.toggle import Toggle
from widgets.combo_store import ComboStore

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from lib.effect import Effect
from lib.set_mapping import add_properties

@add_properties()
class Humanizer(Effect, Gtk.Box):
    hu_auto_sw   = GObject.Property(type=bool, default=False)
    hu_vow1_type    = GObject.Property(type=str)
    hu_vow1_type_idx= GObject.Property(type=int, default=0)
    hu_vow2_type    = GObject.Property(type=str)
    hu_vow2_type_idx= GObject.Property(type=int, default=0)
    hu_sens_lvl     = GObject.Property(type=int, default=0)
    hu_rate_lvl     = GObject.Property(type=int, default=0)
    hu_dept_lvl     = GObject.Property(type=int, default=0)
    hu_effc_lvl     = GObject.Property(type=int, default=0)
    hu_dmix_lvl     = GObject.Property(type=int, default=0)

    def __init__(self, ctrl, pprefx=""):
        super().__init__(ctrl, self.mapping, pprefx)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(6)
        self.parent_prefix = pprefx

        self.auto = Toggle("Picking / Auto")
        self.bind_property(
            "hu_auto_sw", self.auto,
            "active", GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )
        self.append(self.auto)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.append(box)

        self.vow1_list = ComboStore( self, self.types, "hu_vow1_type_idx")
        box.append(self.vow1_list)

        self.vow2_list = ComboStore( self, self.types, "hu_vow2_type_idx")
        box.append(self.vow2_list)

        box = BoxInner("Settings")
        self.append(box)

        self.hu_sens = Slider( "Sens.", "normal", self, "hu_sens_lvl" )
        box.append(self.hu_sens)

        self.hu_rate = Slider( "Rate", "normal", self, "hu_rate_lvl" )
        box.append(self.hu_rate)

        self.hu_dept = Slider( "Depth", "normal", self, "hu_dept_lvl" )
        box.append(self.hu_dept)

        box = BoxInner("Level")
        self.append(box)

        self.hu_effc = Slider( "Effect", "normal", self, "hu_effc_lvl" )
        box.append(self.hu_effc)

        self.hu_dmix = Slider( "Direct Mix", "normal", self, "hu_dmix_lvl" )
        box.append(self.hu_dmix)


