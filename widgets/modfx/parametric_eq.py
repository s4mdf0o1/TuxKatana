import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

from widgets.slider import Slider
from widgets.box_inner import BoxInner

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

class ParametricEqUI(Gtk.Box):
    def __init__(self, own_ctrl):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.own_ctrl = own_ctrl
        
        box_co = BoxInner("Graphic EQ")

        self.pe_loco_lvl = Slider( "Low Cut Off", "low_freq", self.own_ctrl, "pe_loco_lvl" )
        box_co.append(self.pe_loco_lvl)

        self.pe_loga_lvl = Slider( "Low Gain", "gain", self.own_ctrl, "pe_loga_lvl" )
        box_co.append(self.pe_loga_lvl)

        self.pe_lomf_lvl = Slider( "Low Mid Freq", "mid_freq", self.own_ctrl, "pe_lomf_lvl" )
        box_co.append(self.pe_lomf_lvl)

        self.pe_lomq_lvl = Slider( "Low Mid Q", "mid_q", self.own_ctrl, "pe_lomq_lvl" )
        box_co.append(self.pe_lomq_lvl)

        self.pe_lomg_lvl = Slider( "Low Mid Gain", "gain", self.own_ctrl, "pe_lomg_lvl" )
        box_co.append(self.pe_lomg_lvl)

        self.pe_himf_lvl = Slider( "High Mid Freq", "mid_freq", self.own_ctrl, "pe_himf_lvl" )
        box_co.append(self.pe_himf_lvl)

        self.pe_himq_lvl = Slider( "High Mid Q", "mid_q", self.own_ctrl, "pe_himq_lvl" )
        box_co.append(self.pe_himq_lvl)

        self.pe_himg_lvl = Slider( "High Mid Gain", "gain", self.own_ctrl, "pe_himg_lvl" )
        box_co.append(self.pe_himg_lvl)

        self.pe_higa_lvl = Slider( "High Gain", "gain", self.own_ctrl, "pe_higa_lvl" )
        box_co.append(self.pe_higa_lvl)

        self.pe_hico_lvl = Slider( "High Cut Off", "high_freq", self.own_ctrl, "pe_hico_lvl" )
        box_co.append(self.pe_hico_lvl)


        box_lvl = BoxInner("Level")
        self.lev_lvl = Slider( "Level", "gain", self.own_ctrl, "pe_lev_lvl" )
        box_lvl.append(self.lev_lvl)

        self.append(box_co)
        self.append(box_lvl)


