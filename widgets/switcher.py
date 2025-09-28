import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GObject# GLib, Gdk

from ruamel.yaml import YAML
yaml = YAML(typ="rt")
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

        self.bank_a = Bank('BANK_A', config['BANK_A'] )
        self.bank_b = Bank('BANK_B', config['BANK_B'] )
        self.bank_a.f_bank = self.bank_b
        self.bank_b.f_bank = self.bank_a

        self.effects = Bank("EFFECTS", config['EFFECTS'], single=True)

        self.ctrl.connect("status-changed", self.on_status_changed)
        # self.ctrl.mry.connect("notify::re-status", self.on_status_changed)
        # self.ctrl.device.delay.connect("notify::delay-status", self.on_status_changed)

        # self.ctrl.device.mod.connect("notify::mo-status", self.on_status_changed)
        # self.ctrl.device.fx.connect("notify::fx-status", self.on_status_changed)
        self.append(self.effects)
        self.append(self.bank_a)
        self.append(self.bank_b)
        self.ctrl.connect("channel-changed", self.on_channel_changed)

        for bank in [self.bank_a, self.bank_b]:
            for but in bank.buttons:
                but.toggled_id = but.connect("toggled", self.set_channel)
                
                #log.debug(but.name)
                # if but.name == 'BOOSTER':
                #     but.bind_id = self.ctrl.device.booster.bind_property(
                #         "boost_sw", but, "active",
                #         GObject.BindingFlags.BIDIRECTIONAL |\
                #         GObject.BindingFlags.SYNC_CREATE )
                # elif but.name == 'MOD':
                #     but.bind_id = self.ctrl.device.mod.bind_property(
                #         "mo_sw", but, "active",
                #         GObject.BindingFlags.BIDIRECTIONAL |\
                #         GObject.BindingFlags.SYNC_CREATE )
                # elif but.name == 'FX':
                #     but.bind_id = self.ctrl.device.fx.bind_property(
                #         "fx_sw", but, "active",
                #         GObject.BindingFlags.BIDIRECTIONAL |\
                #         GObject.BindingFlags.SYNC_CREATE )

                # elif but.name == 'REVERB':
                #     but.bind_id = self.ctrl.device.reverb.bind_property(
                #         "reverb_sw", but, "active",
                #         GObject.BindingFlags.BIDIRECTIONAL |\
                #         GObject.BindingFlags.SYNC_CREATE )
                # elif but.name == 'DELAY':
                #     but.bind_id = self.ctrl.device.delay.bind_property(
                #         "delay_sw", but, "active",
                #         GObject.BindingFlags.BIDIRECTIONAL |\
                #         GObject.BindingFlags.SYNC_CREATE )
                # else:
            #self.ctrl.device.booster.connect("notify::booster_sw", lambda o,p: print("booster_sw changed:", o.booster_sw))

    def on_status_changed(self, ctrl, obj, bind_prop):
        # log.debug(f"{obj.name} {obj.get_property(bind_prop)=}")
        obj_name = obj.name.lower()
        # status = obj.get_property(bind_prop)
        # name = pspec.name.split('-')[0]
        # log.debug(f"{pspec.name} {name}")
        for but in self.effects.buttons:
            #log.debug(f"{but.name.lower()=}")
            if obj_name == but.name.lower():
                # prefix = obj_name[:3]
                but.bind_id = obj.bind_property(
                    bind_prop, but, "status",
                    GObject.BindingFlags.BIDIRECTIONAL |\
                    GObject.BindingFlags.SYNC_CREATE )
                but.disconnect(but.handler_id)
                obj_sw = obj.find_property(obj_name+'_sw')
                if obj_sw:
                    # log.debug(f"{obj_sw.name=}")
                    but.bind_id = obj.bind_property(
                        obj_sw.name.replace('-', '_'), but, "active",
                        GObject.BindingFlags.BIDIRECTIONAL |\
                        GObject.BindingFlags.SYNC_CREATE )
                # status = obj.get_property(pspec.name)
                # but.set_status_id(status)

    def set_channel( self, button):
        log.debug(f"{button.name}: {button.data}")
        if button.get_active():
            if 'CH_' in button.name:
                self.ctrl.set_midi_channel(button.data)

    def on_channel_changed(self, obj, ch_num):
        # log.debug(f"{obj} {ch_num=}")
        if ch_num <= 4:
            but = self.bank_a.buttons[ch_num-1]
            if hasattr(but, 'toggled_id'):
                but.handler_block(but.toggled_id)
            but.set_active(True)
            if hasattr(but, 'toggled_id'):
                but.handler_unblock(but.toggled_id)
        else:
            but = self.bank_b.buttons[ch_num-5]
            # but.handler_block(but.toggled_id)
            but.set_active(True)
            # but.handler_unblock(but.toggled_id)
            # self.bank_b.buttons[ch_num-5].set_active(True)
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

