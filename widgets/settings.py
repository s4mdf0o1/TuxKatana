import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject
#import mido

from ruamel.yaml import YAML
yaml = YAML(typ="safe")
config = ""
with open("params/config.yaml", "r") as f:
    config = yaml.load(f)
dots = config['DOTS']

import logging
dbg=logging.getLogger("debug")

from .slider import Slider

from .presets import PresetsView
from .amplifier import Amplifier
from .booster import Booster
from .debug import Debug

class KS_TabbedPanel(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        self.stack = Gtk.Stack()
        self.stack.set_transition_duration(150)

        sidebar = Gtk.StackSidebar()
        sidebar.set_stack( self.stack )
        self.set_vexpand(True)

        self.append(sidebar)
        self.append(self.stack)

    def add_tab(self, widget, name, title):
        self.stack.add_titled(widget, name, title)

    def set_active_tab(self, name):
        self.stack.set_visible_child_name(name)


class KS_Settings(Gtk.Box):
    def __init__(self, name, ctrl):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.ctrl = ctrl
        if name == "DEBUG":
            debug = Debug(ctrl)
            self.append(debug)
        elif name == "PRE-AMP":
            self.amplifier = Amplifier(ctrl)
            self.append(self.amplifier) 
        elif name == "BOOSTER":
            self.booster = Booster(ctrl)
            self.append(self.booster)
        else:
            self.slider = Slider( "Level", 50)
            self.append(self.slider)

class Settings(Gtk.Box):
    def __init__(self, label, ctrl):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.get_style_context().add_class("inner")
        self.ctrl = ctrl
        self.title = Gtk.Label(label=label)
        self.append(self.title)
        ctrl.device.bind_property("name", self.title, \
                "label", GObject.BindingFlags.DEFAULT)
        #box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        tabs = KS_TabbedPanel()
        for name in ["PRESETS","PRE-AMP", "BOOSTER", "MOD", "FX", "DELAY", "REVERB", "CHAIN", "DEBUG"]:
            page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            tabs.add_tab(page, name.lower(), name)
            if name == "PRESETS":
                self.presets = PresetsView(ctrl)
                page.append(self.presets)
            else:
                ks_settings = KS_Settings( name, ctrl)
                page.append(ks_settings)

        #page2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        #page2.append(Gtk.Label(label="Contenu de l’onglet 2"))
        #tabs.add_tab(page2, "tab2", "MOB")

        tabs.set_active_tab("debug")
        #box.append(tabs)
        self.append(tabs)
        
        #self.booster = Slider( "Level", 50)
        #Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 127, 1)
        #self.bass_slider.connect("value-changed", self.on_bass_changed)
        #page1.append(self.booster)


