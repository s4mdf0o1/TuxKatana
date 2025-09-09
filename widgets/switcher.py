import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GObject# GLib, Gdk

from ruamel.yaml import YAML
yaml = YAML(typ="safe")
config = ""
with open("params/config.yaml", "r") as f:
    config = yaml.load(f)
dots = config['DOTS']

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from .toggle import Toggle
from .bank import Bank

class Switcher(Gtk.Box):
    def __init__(self, config, ctrl):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.ctrl = ctrl

        self.bank_a = Bank('BANK_A', config['BANK_A'], ctrl )
        self.bank_b = Bank('BANK_B', config['BANK_B'], ctrl )
        self.bank_a.f_bank = self.bank_b
        self.bank_b.f_bank = self.bank_a

        #self.effects = Effects('EFFECTS', config, ctrl)
        self.effects = Bank("EFFECTS", config['EFFECTS'], ctrl, True)

        self.ctrl.device.booster.connect("notify::booster-status", self.on_status_changed)

        self.append(self.effects)
        self.append(self.bank_a)
        self.append(self.bank_b)
        self.ctrl.device.mry.connect("channel-changed", self.on_channel_changed)

        for bank in [self.bank_a, self.bank_b, self.effects]:
            for but in bank.buttons:
                #log.debug(but.name)
                if but.name == 'BOOSTER':
                    self.ctrl.device.booster.bind_property(
                        "booster_sw", but, "active",
                        GObject.BindingFlags.BIDIRECTIONAL |\
                        GObject.BindingFlags.SYNC_CREATE )
                else:
                    but.toggled_id = but.connect("toggled", self.callback_toggled)

    def on_status_changed(self, obj, pspec):
        name = pspec.name.split('-')[0]
        #log.debug(f"{pspec.name} {name}")
        for but in self.effects.buttons:
            #log.debug(f"{but.name.lower()=}")
            if name == but.name.lower():
                status = obj.get_property(pspec.name)
                but.set_status_id(status)

    def callback_toggled( self, button):
        #log.debug(button.path)
        if button.get_active():
            self.ctrl.set_on( button.path )
        else:
            self.ctrl.set_off(button.path)

    def on_channel_changed(self, obj, ch_num):
        log.debug(f"{ch_num=}")
        if ch_num <= 4:
            self.bank_a.buttons[ch_num-1].set_active(True)
        else:
            self.bank_b.buttons[ch_num-5].set_active(True)
        #self.presets[ch_num-1].set_active(True)


class Effects(Gtk.Box):
    def __init__(self, label, cfg, ctrl):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.get_style_context().add_class("inner")
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        label = Gtk.Label(label=label)
        self.append(label)
        self.append(box)
        self.ctrl = ctrl
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
            self.ctrl.set_on(button.path)
            button.is_active = False
        else:
            self.ctrl.set_off(button.path)
            button.is_active = True

#class KES_Bank(Gtk.Box):
#    def __init__(self, label, buttons, ctrl):
#        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
#        self.get_style_context().add_class("inner")
#        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
#        label = Gtk.Label(label=label)
#        self.append(label)
#        self.append(box)
#        self.ctrl = ctrl
#        self.presets = []
#        for b in buttons:
#            preset = Toggle( b, buttons[b] )
#            preset.handler_id = preset.connect("toggled", self.on_toggled)
#            self.presets.append(preset)
#            box.append( preset )
#            
#    def on_toggled(self, widget):
#        self.ctrl.set_on( widget.path )
#        self.set_inactives( widget )
#        self.f_bank.set_inactives()
#
#    def set_inactives( self, widget=None ):
#        for button in self.presets:
#            if button != widget and button.get_active():
#                button.handler_block(button.handler_id)
#                button.set_active(False)
#                button.handler_unblock(button.handler_id)


