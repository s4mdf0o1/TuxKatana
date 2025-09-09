import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

from .slider import Slider
from .tabbed_panel import TabbedPanel
from .bank import Bank
from .toggle import Toggle
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

#from ruamel.yaml import YAML
#yaml = YAML(typ="rt")
#from .toggle import Toggle

class Booster(Gtk.Box):
    def __init__(self, ctrl):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.ctrl = ctrl
        self.own_ctrl = self.ctrl.device.booster
        
        banks = {"GREEN":'1', "RED":'2', "YELLOW":'3'}
        self.bank_select = Bank("BOOSTER", banks, ctrl)
        self.bank_select.buttons[0].set_status_id(1)
        self.bank_select.buttons[2].set_status_id(3)
        self.append(self.bank_select)

        self.own_ctrl.bind_property(
            "bank_select", self.bank_select, "selected",
            GObject.BindingFlags.BIDIRECTIONAL |\
            GObject.BindingFlags.SYNC_CREATE )

        self.store = Gtk.ListStore(int, str, str)
        self.models = Gtk.ComboBox.new_with_model(self.store)
        renderer = Gtk.CellRendererText()
        self.models.pack_start(renderer, True)
        self.models.add_attribute(renderer, "text", 1)
        self.append(self.models)
        self.own_ctrl.bind_property(
            "model_num", self.models, "active", 
            GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )

        box_drive = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        box_drive.get_style_context().add_class('inner')
        label=Gtk.Label(label="Drive")
        label.set_xalign(1.0)
        label.set_margin_end(20)
        box_drive.append(label)

        self.drive_lvl = Slider( "Drive", 50.0, self.own_ctrl, "drive_lvl" )
        self.drive_lvl.name = "drive_lvl"
        self.drive_lvl.connect("value-changed", self.on_slider_changed)
        box_drive.append(self.drive_lvl)

        self.bottom_lvl = Slider( "Bottom", 50.0, self.own_ctrl, "bottom_lvl" )
        self.bottom_lvl.name = "bottom_lvl"
        self.bottom_lvl.connect("value-changed", self.on_slider_changed)
        box_drive.append(self.bottom_lvl)

        self.tone_lvl = Slider( "Tone", 50.0, self.own_ctrl, "tone_lvl" )
        self.tone_lvl.name = "tone_lvl"
        self.tone_lvl.connect("value-changed", self.on_slider_changed)
        box_drive.append(self.tone_lvl)

        self.append(box_drive)

        box_level = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        box_level.get_style_context().add_class('inner')
        label=Gtk.Label(label="Level")
        label.set_xalign(1.0)
        label.set_margin_end(20)
        box_level.append(label)

        self.effect_lvl = Slider( "Effect", 50.0, self.own_ctrl, "effect_lvl" )
        self.effect_lvl.name = "effect_lvl"
        self.effect_lvl.connect("value-changed", self.on_slider_changed)
        box_level.append(self.effect_lvl)

        self.dir_mix_lvl = Slider( "Dir Mix", 50.0, self.own_ctrl, "dir_mix_lvl" )
        self.dir_mix_lvl.name = "dir_mix_lvl"
        self.dir_mix_lvl.connect("value-changed", self.on_slider_changed)
        box_level.append(self.dir_mix_lvl)

        self.append(box_level)

        box_solo = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        box_solo.get_style_context().add_class('inner')
        label=Gtk.Label(label="Solo")
        label.set_xalign(1.0)
        label.set_margin_end(20)
        box_solo.append(label)


        self.solo_lvl = Slider( "Level", 50.0, self.own_ctrl, "solo_lvl" )
        self.solo_lvl.name = "solo_lvl"
        self.solo_lvl.connect("value-changed", self.on_slider_changed)
        box_solo.append(self.solo_lvl)
        self.append(box_solo)

        self.solo_sw = Toggle("SOLO")
        box_solo.append(self.solo_sw)

        self.own_ctrl.connect("booster-loaded", self.on_booster_models_loaded)

    def on_slider_changed( self, slider):
        self.own_ctrl.set_property(slider.name, slider.get_value())

#    def on_booster_models_loaded(self, device, models):
#        i = 0
#        for name, code in models.items():
#            self.store.append([i,name, code])
#            i += 1


