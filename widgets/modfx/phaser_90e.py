
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

from widgets.slider import Slider
from widgets.box_inner import BoxInner
from widgets.toggle import Toggle

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from lib.effect import Effect
from lib.set_mapping import add_properties

@add_properties()
class Phaser90e(Effect, Gtk.Box):
    p9_script_sw    = GObject.Property(type=bool, default=False)
    p9_speed_lvl    = GObject.Property(type=int, default=0)
    p9_levl_lvl     = GObject.Property(type=int, default=0)

    def __init__(self, ctrl, pprefx=""):
        super().__init__(ctrl, self.mapping, pprefx)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(10)
        self.parent_prefix = pprefx

        box = BoxInner("Phaser 90E")
        self.append(box)

        self.p9_script = Toggle("Script ON/OFF")
        self.bind_property(
            "p9_script_sw", self.p9_script,
            "active", GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )
        box.append(self.p9_script)

        box = BoxInner("Settings")
        self.append(box)

        self.p9_speed = Slider( "Speed", "normal", self, "p9_speed_lvl" )
        box.append(self.p9_speed)

        box = BoxInner("Level")
        self.append(box)

        self.p9_levl = Slider( "Level", "normal", self, "p9_levl_lvl" )
        box.append(self.p9_levl)


