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

from widgets.tuner_dialog import * #s tun_dial

from .slider import Slider

from .presets import PresetsView
from .amplifier import Amplifier
from .booster import Booster
from .mod_fx import Mod, Fx
from .reverb import Reverb
from .delay import Delay
from .delay_reverb import DelayReverb
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
        elif name == "MOD":
            self.mod = Mod(ctrl)
            self.append(self.mod)
        elif name == "FX":
            self.fx = Fx(ctrl)
            self.append(self.fx)
        elif name == "REVERB":
            self.reverb = Reverb(ctrl)
            self.append(self.reverb)
        elif name == "DELAY":
            self.delay = Delay(ctrl)
            self.append(self.delay)
        elif name == "DELAY_R":
            self.delay_r = DelayReverb(ctrl)
            self.append(self.delay_r)


        else:
            label = Gtk.Label(label="WIP")
            self.append(label)

class CommLabel(Gtk.Label):
    def __init__(self, device):
        self.states = [ "⚫", "🟢", "🔴", "🟡" ]
        self.state = 0
        # self.device = device
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
        self.comm = CommLabel(ctrl)

        self.tuner_b= Gtk.Button(label=">🎸<")
        self.tuner_b.set_halign(Gtk.Align.START)
        self.tuner_b.get_style_context().add_class('edit-mode')
        self.tuner_b.set_tooltip_text("Tuner Dialog")
        self.tuner_b.connect("clicked", self.open_tuner)
       
        self.title = Gtk.Label(label=label)
        self.title.set_halign(Gtk.Align.CENTER)
        self.title.set_hexpand(True)
        self.edit_tog = Gtk.ToggleButton(label=" ⚠️ ")
        self.edit_tog.set_halign(Gtk.Align.END)
        self.edit_tog.get_style_context().add_class('edit-mode')
        self.edit_tog.set_tooltip_text("Toggle Edit Mode")
        self.edit_tog.connect("toggled", self.toggle_edit_mode)
        ctrl.bind_property("edit_mode", self.edit_tog, \
                "active", GObject.BindingFlags.SYNC_CREATE | \
                GObject.BindingFlags.BIDIRECTIONAL)
        h_box.append(self.comm)
        h_box.append(self.tuner_b)
        h_box.append(self.title)
        h_box.append(self.edit_tog)
        self.append(h_box)
        ctrl.bind_property("name", self.title, \
                "label", GObject.BindingFlags.DEFAULT)

        tabs = KS_TabbedPanel()
        for name in ["PRESETS","PRE-AMP", "BOOSTER", "MOD", "FX", "DELAY", "REVERB","DELAY_R", "CHAIN", "DEBUG"]:
            page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            tabs.add_tab(page, name.lower(), name)
            if name == "PRESETS":
                self.presets = PresetsView(ctrl)
                page.append(self.presets)
            else:
                ks_settings = KS_Settings( name, ctrl)
                page.append(ks_settings)

        tabs.set_active_tab("presets")
        self.append(tabs)
        
    def toggle_edit_mode(self, button):
        edit = self.edit_tog.get_active()
        self.ctrl.set_edit_mode(edit)

    def open_tuner(self, btn):
        # import threading
        # import sounddevice as sd
        # log.debug(btn)
        self.ctrl.parent.win.set_sensitive(False)
        # global stop_flag; stop_flag=False
        self.tuner=TunerDialog(self, btn.get_root())
        self.tuner.connect("response", lambda d,r: self.stop_tuner(d))
        self.tuner.present()
        threading.Thread(target=self.tuner.processing_thread, args=(self.tuner,), daemon=True).start()
        device_index = self.tuner.find_katana_device()
        self.stream = sd.InputStream(
                device=device_index, 
                channels=1, 
                samplerate=FS, 
                blocksize=BLOCKSIZE, 
                callback=self.tuner.audio_callback
            )
        self.stream.start()

    def stop_tuner(self, dialog):
        # global stop_flag; stop_flag=True
        self.stream.stop(); self.stream.close()
        self.tuner.close()
        self.ctrl.parent.win.set_sensitive(True)


