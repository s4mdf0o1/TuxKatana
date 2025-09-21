import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

# from .slider import Slider
from widgets.slider import Slider
# from .tabbed_panel import TabbedPanel
# from .bank import Bank
from widgets.toggle import Toggle
from widgets.box_inner import BoxInner

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

class PedalWahUI(Gtk.Box):
    def __init__(self, own_ctrl):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.own_ctrl = own_ctrl
        
        # box_sel = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        box_pw = BoxInner("Pedal Wah")

        # box_sel.append(self.types)
        self.types_store = Gtk.ListStore(int, str, str)
        self.types = Gtk.ComboBox.new_with_model(self.types_store)
        self.types.set_hexpand(True)
        renderer = Gtk.CellRendererText()
        self.types.pack_start(renderer, True)
        self.types.add_attribute(renderer, "text", 1)
        self.own_ctrl.bind_property(
            "pw_type_idx", self.types, "active", 
            GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )
        box_pw.append(self.types)

        self.pos_lvl = Slider( "Pos", "normal", self.own_ctrl, "pw_pos_lvl" )
        self.pos_lvl.name = "pw_pos_lvl"
        self.pos_lvl.connect("delayed-value", self.on_slider_changed)
        box_pw.append(self.pos_lvl)

        self.min_lvl = Slider( "Min", "normal", self.own_ctrl, "pw_min_lvl" )
        self.min_lvl.name = "pw_min_lvl"
        self.min_lvl.connect("delayed-value", self.on_slider_changed)
        box_pw.append(self.min_lvl)

        self.max_lvl = Slider( "Max", "normal", self.own_ctrl, "pw_max_lvl" )
        self.max_lvl.name = "pw_max_lvl"
        self.max_lvl.connect("delayed-value", self.on_slider_changed)
        box_pw.append(self.max_lvl)

        box_lvl = BoxInner("Level")
        self.eff_lvl = Slider( "Effect", "normal", self.own_ctrl, "pw_eff_lvl" )
        self.eff_lvl.name = "pw_eff_lvl"
        self.eff_lvl.connect("delayed-value", self.on_slider_changed)
        box_lvl.append(self.eff_lvl)

        self.dmix_lvl = Slider( "Direct Mix", "normal", self.own_ctrl, "pw_dmix_lvl" )
        self.dmix_lvl.name = "pw_dmix_lvl"
        self.dmix_lvl.connect("delayed-value", self.on_slider_changed)
        box_lvl.append(self.dmix_lvl)

        # self.append(box_sel)
        self.append(box_pw)
        self.append(box_lvl)

        #self.own_ctrl.connect("pedalwah-map-ready", self.on_pedalwah_loaded)
        self.load_types( self.own_ctrl.map['PWTypes'])

    # def on_pedalwah_loaded(self, own_ctrl, types):
    #     log.debug(f"{types}")
    #     i = 0
    #     for name, code in types.items():
    #         self.types_store.append([i,name, code])
    #         i += 1

    def load_types(self, types):
        i = 0
        for name, code in types.items():
            self.types_store.append([i,name, code])
            i += 1
        # log.debug(f"{self.own_ctrl.pw_type} {self.own_ctrl.pw_type_idx}")
        self.types.set_active(self.own_ctrl.pw_type)
       
    def on_slider_changed( self, slider, value):
        old_val = self.own_ctrl.get_property(slider.name)
        value = int(value)
        # log.debug(f"{old_val} {value}")
        if value != old_val:
            self.own_ctrl.set_property(slider.name, int(value))


