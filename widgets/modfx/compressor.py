import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

from widgets.slider import Slider
# from .tabbed_panel import TabbedPanel
# from .bank import Bank
from widgets.toggle import Toggle
from widgets.box_inner import BoxInner
from widgets.combo_store import ComboStore

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

class CompressorUI(Gtk.Box):
    def __init__(self, own_ctrl):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.own_ctrl = own_ctrl
        
        box_co = BoxInner("Compressor")
        self.types = ComboStore( own_ctrl, 'Types', True)
                # own_ctrl, "co_type_idx", "", 'Types', 'co_type')
        # self.types_store = Gtk.ListStore(int, str, str)
        # self.types = Gtk.ComboBox.new_with_model(self.types_store)
        # self.types.set_hexpand(True)
        # renderer = Gtk.CellRendererText()
        # self.types.pack_start(renderer, True)
        # self.types.add_attribute(renderer, "text", 1)
        # self.own_ctrl.bind_property(
        #     "co_type_idx", self.types, "active", 
        #     GObject.BindingFlags.SYNC_CREATE |\
        #     GObject.BindingFlags.BIDIRECTIONAL )
        box_co.append(self.types)

        self.sus_lvl = Slider( "Sustain", "normal", self.own_ctrl, "co_sus_lvl" )
        box_co.append(self.sus_lvl)

        self.att_lvl = Slider( "Attack", "normal", self.own_ctrl, "co_att_lvl" )
        box_co.append(self.att_lvl)

        self.tone_lvl = Slider( "Tone", "normal", self.own_ctrl, "co_tone_lvl" )
        box_co.append(self.tone_lvl)

        box_lvl = BoxInner("Level")
        self.eff_lvl = Slider( "Effect", "normal", self.own_ctrl, "co_eff_lvl" )
        box_lvl.append(self.eff_lvl)

        # self.dmix_lvl = Slider( "Direct Mix", "normal", self.own_ctrl, "co_dmix_lvl" )
        # box_lvl.append(self.dmix_lvl)

        self.append(box_co)
        self.append(box_lvl)

        # self.load_types( self.own_ctrl.map['Types'])

    # def load_types(self, types):
    #     i = 0
    #     for name, code in types.items():
    #         self.types_store.append([i,name, code])
    #         i += 1
    #     self.types.set_active(self.own_ctrl.co_type)
       
    # def on_slider_changed( self, slider, value):
    #     old_val = self.own_ctrl.get_property(slider.name)
    #     value = int(value)
    #     if value != old_val:
    #         self.own_ctrl.set_property(slider.name, int(value))


