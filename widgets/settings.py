import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

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
from .amplifier import AmplifierUI
from .booster import BoosterUI
from .reverb import ReverbUI
from .delay import DelayUI
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
            self.amplifier = AmplifierUI(ctrl.device.amplifier)
            self.append(self.amplifier) 
        elif name == "BOOSTER":
            self.booster = BoosterUI(ctrl.device.booster)
            self.append(self.booster)
        elif name == "REVERB":
            self.reverb = ReverbUI(ctrl.device.reverb)
            self.append(self.reverb)
        elif name == "DELAY":
            self.delay = DelayUI(ctrl.device.delay)
            self.append(self.delay)

        else:
            self.slider = Slider( "Level", "normal")
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

        tabs.set_active_tab("debug")
        self.append(tabs)
        


