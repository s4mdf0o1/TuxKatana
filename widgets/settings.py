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
from .modfx_ui import ModFxUI
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
        elif name == "MOD":
            self.mod = ModFxUI(ctrl, ctrl.device.mod, name)
            self.append(self.mod)
        elif name == "FX":
            self.fx = ModFxUI(ctrl, ctrl.device.fx, name)
            self.append(self.fx)
        elif name == "REVERB":
            self.reverb = ReverbUI(ctrl.device.reverb)
            self.append(self.reverb)
        elif name == "DELAY":
            self.delay = DelayUI(ctrl.device.delay)
            self.append(self.delay)

        else:
            label = Gtk.Label(label="WIP")
            self.append(label)

class CommLabel(Gtk.Label):
    def __init__(self, device):
        self.states = [ "⚫", "🟢", "🔴", "🟡" ]
        self.state = 0
        self.device = device
        super().__init__(label=self.states[0])
        self.set_halign(Gtk.Align.START)
        self.get_style_context().add_class('comm')
        device.bind_property("comm", self, "label",\
                GObject.BindingFlags.DEFAULT, \
                self._switch)#SYNC_CREATE)

    def _switch(self, binding, value):
        self.set_label(self.states[value])

class Settings(Gtk.Box):
    def __init__(self, label, ctrl):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.get_style_context().add_class("inner")
        self.ctrl = ctrl
        h_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        self.comm = CommLabel(ctrl.device)
        self.title = Gtk.Label(label=label)
        self.title.set_halign(Gtk.Align.CENTER)
        self.title.set_hexpand(True)
        self.edit_tog = Gtk.ToggleButton(label=" ⚠️ ")
        self.edit_tog.set_halign(Gtk.Align.END)
        self.edit_tog.get_style_context().add_class('edit-mode')
        self.edit_tog.set_tooltip_text("Toggle Edit Mode")
        self.edit_tog.connect("toggled", self.toggle_edit_mode)
        ctrl.device.bind_property("edit_mode", self.edit_tog, \
                "active", GObject.BindingFlags.SYNC_CREATE | \
                GObject.BindingFlags.BIDIRECTIONAL)
        h_box.append(self.comm)
        h_box.append(self.title)
        h_box.append(self.edit_tog)
        self.append(h_box)
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
        
    def toggle_edit_mode(self, button):
        edit = self.edit_tog.get_active()
        self.ctrl.device.set_edit_mode(edit)

