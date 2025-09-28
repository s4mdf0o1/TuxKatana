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
class ParametricEq(Effect, Gtk.Box):
    pe_loco_lvl = GObject.Property(type=int, default=0)
    pe_loga_lvl = GObject.Property(type=int, default=0)
    pe_lomf_lvl = GObject.Property(type=int, default=0)
    pe_lomq_lvl = GObject.Property(type=int, default=0)
    pe_lomg_lvl = GObject.Property(type=int, default=0)
    pe_himf_lvl = GObject.Property(type=int, default=0)
    pe_himq_lvl = GObject.Property(type=int, default=0)
    pe_himg_lvl = GObject.Property(type=int, default=0)
    pe_higa_lvl = GObject.Property(type=int, default=0)
    pe_hico_lvl = GObject.Property(type=int, default=0)
    pe_lev_lvl  = GObject.Property(type=int, default=0)

    def __init__(self, ctrl, pprefx=""):
        super().__init__(ctrl, self.mapping, pprefx)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(3)
        self.parent_prefix = pprefx
        
        box_co = BoxInner()

        self.pe_loco= Slider( "Low Cut Off", "low_freq", self, "pe_loco_lvl" )
        box_co.append(self.pe_loco)

        self.pe_loga= Slider( "Low Gain", "gain", self, "pe_loga_lvl" )
        box_co.append(self.pe_loga)

        self.pe_lomf= Slider( "Low Mid Freq", "mid_freq", self, "pe_lomf_lvl" )
        box_co.append(self.pe_lomf)

        self.pe_lomq= Slider( "Low Mid Q", "mid_q", self, "pe_lomq_lvl" )
        box_co.append(self.pe_lomq)

        self.pe_lomg= Slider( "Low Mid Gain", "gain", self, "pe_lomg_lvl" )
        box_co.append(self.pe_lomg)

        self.pe_himf= Slider( "High Mid Freq", "mid_freq", self, "pe_himf_lvl" )
        box_co.append(self.pe_himf)

        self.pe_himq= Slider( "High Mid Q", "mid_q", self, "pe_himq_lvl" )
        box_co.append(self.pe_himq)

        self.pe_himg= Slider( "High Mid Gain", "gain", self, "pe_himg_lvl" )
        box_co.append(self.pe_himg)

        self.pe_higa= Slider( "High Gain", "gain", self, "pe_higa_lvl" )
        box_co.append(self.pe_higa)

        self.pe_hico= Slider( "High Cut Off", "high_freq", self, "pe_hico_lvl" )
        box_co.append(self.pe_hico)


        box_lvl = BoxInner()
        self.lev= Slider( "Level", "gain", self, "pe_lev_lvl" )
        box_lvl.append(self.lev)

        self.append(box_co)
        self.append(box_lvl)


