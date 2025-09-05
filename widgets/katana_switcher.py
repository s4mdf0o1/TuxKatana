import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk

from ruamel.yaml import YAML
yaml = YAML(typ="safe")
config = ""
with open("params/config.yaml", "r") as f:
    config = yaml.load(f)
dots = config['DOTS']

import logging
from lib.log_setup import LOGGER_NAME
logger = logging.getLogger(LOGGER_NAME)

from .toggle import Toggle

class KatanaEffectSwitcher(Gtk.Box):
    def __init__(self, config, katana):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.katana = katana
        self.bank_a = KES_Bank('BANK_A', config['BANK_A'], katana )
        self.bank_b = KES_Bank('BANK_B', config['BANK_B'], katana )
        self.bank_a.f_bank = self.bank_b
        self.bank_b.f_bank = self.bank_a
        self.effects = KES_Effects('EFFECTS', config, katana)

        #panel_button = KES_Toggle('PANEL', config['PANEL'], katana)
        #panel_button.connect("toggled", self.on_panel_toggle)
        #effects_button = KES_Toggle('EFFECTS', config['EFFECTS'], katana)
        #effects_button.connect("toggled", self.on_effects_toggle)

        self.append(self.effects)
        self.append(self.bank_a)
        self.append(self.bank_b)

#class KES_Switch(Gtk.Button):
#    def __init__(self, label, katana):
        
class KES_Effects(Gtk.Box):
    def __init__(self, label, cfg, katana):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.get_style_context().add_class("inner")
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        label = Gtk.Label(label=label)
        self.append(label)
        self.append(box)
        self.katana = katana
        effects = ["BOOSTER", "MOD", "FX", "DELAY", "REVERB"]
        for name in effects:
            but = Toggle(name, cfg[name], status_id=1)
            #colors = [c for n,c in dots.items()]
            #label = colors[effects.index(name)%4] + "  " + name
            #but = Gtk.Button(label= config['DOTS']['BLACK'] + "  " +name)
            #but = Gtk.Button(label= label)
            #but.name = name
            #but.get_style_context().add_class("outer")
            #but.path = cfg[name]
            #but.is_active = False
            but.connect("clicked", self.on_click)
            #but.set_hexpand(True)
            #but.set_halign(Gtk.Align.FILL)

            box.append(but)

    def on_click( self, button ):
        if button.get_active():
            logger.debug(button.name)
            self.katana.set_on(button.path)
            button.is_active = False
        else:
            self.katana.set_off(button.path)
            button.is_active = True

class KES_Bank(Gtk.Box):
    def __init__(self, label, buttons, katana):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.get_style_context().add_class("inner")
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        label = Gtk.Label(label=label)
        self.append(label)
        self.append(box)
        self.katana = katana
        self.presets = []
        for b in buttons:
            preset = Toggle( b, buttons[b] )
            preset.handler_id = preset.connect("toggled", self.on_toggled)
            self.presets.append(preset)
            box.append( preset )

    def on_toggled(self, widget):
        self.katana.set_on( widget.path )
        self.set_inactives( widget )
        self.f_bank.set_inactives()

    def set_inactives( self, widget=None ):
        for button in self.presets:
            if button != widget and button.get_active():
                button.handler_block(button.handler_id)
                button.set_active(False)
                button.handler_unblock(button.handler_id)


