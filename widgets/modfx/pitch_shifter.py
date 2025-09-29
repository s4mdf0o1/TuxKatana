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
class PitchShifter(Effect, Gtk.Box):
    ps_type         = GObject.Property(type=str)
    ps_type_idx     = GObject.Property(type=int, default=0)
    ps_mode_sw      = GObject.Property(type=bool, default=False)
    ps_pred_lvl     = GObject.Property(type=float, default=0.0)
    ps_pitch_lvl    = GObject.Property(type=int, default=0)
    ps_fine_lvl     = GObject.Property(type=int, default=0)
    ps_fb_lvl       = GObject.Property(type=int, default=0)
    ps_voc1_lvl     = GObject.Property(type=int, default=0)
    ps_dirc_lvl     = GObject.Property(type=int, default=0)
    def __init__(self, ctrl, pprefx=""):
        super().__init__(ctrl, self.mapping, pprefx)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(6)
        self.parent_prefix = pprefx

        # box_ps = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)

        box = BoxInner("Pitch Shifter", h_box=True)
        self.append(box)

        self.types_list = ComboStore( self, self.types, "ps_type_idx")
        self.types_list.set_hexpand(True)
        box.h_box.append(self.types_list)

        self.ps_mode = Toggle("One/Two Voice.s Mono")
        self.ps_mode.set_hexpand(False)
        self.bind_property(
            "ps_mode_sw", self.ps_mode,
            "active", GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )
        box.h_box.append(self.ps_mode)

        box_lv = BoxInner("Levels")
        self.append(box_lv)

        self.pred = Slider( "Pre Delay", "time_300ms", self, "ps_pred_lvl" )
        box_lv.append(self.pred)

        self.pitch = Slider( "Pitch", "normal", self, "ps_pitch_lvl" )
        box_lv.append(self.pitch)

        self.fine = Slider( "Fine", "normal", self, "ps_fine_lvl" )
        box_lv.append(self.fine)

        self.fb = Slider( "Feedback", "normal", self, "ps_fb_lvl" )
        box_lv.append(self.fb)

        self.voc1= Slider( "Voice 1", "normal", self, "ps_voc1_lvl" )
        box_lv.append(self.voc1)

        self.dirc = Slider( "Direct Mix", "normal", self, "ps_dirc_lvl" )
        box_lv.append(self.dirc)

