#!/usr/bin/env python3
import sys
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk

import mido
from threading import Thread
from ruamel.yaml import YAML
yaml = YAML(typ="safe")
from time import sleep

from KatanaController import KatanaController
from widgets import KatanaEffectSwitcher, KatanaSettings
from lib.log_setup import setup_logger
logger = setup_logger("logs/katana_session.log")

class ConnectWait(Gtk.Dialog):
    def __init__(self, app, parent):
        super().__init__(title="Connexion", transient_for=parent, modal=True)
        self.set_default_size(300, 100)
        self.set_decorated(False)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.get_style_context().add_class("bordered")

        label = Gtk.Label(label="Appareil Déconnecté...")
        spinner = Gtk.Spinner()
        spinner.start()
        button=Gtk.Button(label="Quitter")
        button.connect("clicked", lambda *_: app.quit())

        box.append(label)
        box.append(spinner)
        box.append(button)
        self.set_child(box)

class MainWindow(Gtk.Window):
    def __init__(self, app, config):
        super().__init__(application=app)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_child(box)

        self.ks = KatanaSettings( "SETTINGS", config['SETTINGS'], app.katana)
        box.append(self.ks)
        self.kes = KatanaEffectSwitcher( config['KES'], app.katana)
        box.append(self.kes)

        self.wait_dialog = ConnectWait( app, self )
        self.set_sensitive(False)
        self.wait_dialog.present()
        GLib.timeout_add_seconds(1, self.check_connection)

    def check_connection( self ):
        print("MainWindow.check_connection")
        if app.katana.port.has_device:
            self.set_sensitive(True)
            self.wait_dialog.set_visible(False)
            return False
        #else:
            #self.set_sensitive(False)
            #self.wait_dialog.set_visible(True)
        return True

    def set_device_name( self, name ):
        pass

class TuxKatana(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.domosys.TuxKatana")

    def do_activate(self):
        config = {}
        with open("params/config.yaml", "r") as f:
            config = yaml.load(f)
        self.dots=config['DOTS']
        self.katana = KatanaController(self)
        self.win = MainWindow(self, config)
        self.win.set_default_size(550, 650)
        self.win.set_title("Tux Katana")
        self.win.set_resizable(True)
        #win.maximize()

        css_provider = Gtk.CssProvider()
        css_provider.load_from_path("style.css")

        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor()
        geometry = monitor.get_geometry()

        x = (geometry.width - 800) // 2
        y = (geometry.height - 600) // 2
        #self.move(x, y)
        self.win.present()


if __name__ == "__main__":
    app = TuxKatana()
    app.run(sys.argv)


