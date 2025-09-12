#!/usr/bin/env python3
import sys
import argparse
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

import mido
from threading import Thread
from ruamel.yaml import YAML
yaml = YAML(typ="safe")
from time import sleep

from lib import Controller

from widgets import Switcher, Settings, ConnectWait

import logging
from lib.log_setup import setup_logger
log = setup_logger()

def close(app):
    log.info(f"Closing...")
    #app.ctrl.port.close()

class MainWindow(Gtk.Window):
    def __init__(self, app, config):
        super().__init__(application=app)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_child(box)
        self.app = app

        #self.settings = Settings( "SETTINGS", config['SETTINGS'], app.ctrl)
        self.settings = Settings( "SETTINGS", app.ctrl)
        box.append(self.settings)
        self.switcher = Switcher( config['SWITCHER'], app.ctrl)
        box.append(self.switcher)
        app.emit("main-ready")

        self.wait_dialog = ConnectWait( app, self )
        self.set_sensitive(False)
        self.wait_dialog.present()
        GLib.timeout_add_seconds(1, self.check_connection)

    def check_connection( self ):
        log.debug("check_connection")
        if self.app.ctrl.port.has_device:
            self.set_sensitive(True)
            self.wait_dialog.set_visible(False)
            return False
        return True

    def set_device_name( self, name ):
        pass

class TuxKatana(Gtk.Application):
    __gsignals__ = {
        "main-ready": (GObject.SIGNAL_RUN_FIRST, None, ()),
    }
    def __init__(self, debug=False, sysex=False):
        super().__init__(application_id="org.domosys.TuxKatana")
        self.debug=debug
        self.sysex=sysex
        if sysex:
            log.info("SysEx Messages logged in ./logs/sysex.log")
        elif debug:
            log.info("Debug logging in terminal only")
        log.info("Logging INFO/WARNING/... in ./logs/tuxkatana.log")

    def do_activate(self):
        config = {}
        with open("params/config.yaml", "r") as f:
            config = yaml.load(f)
        self.dots=config['DOTS']

        self.ctrl = Controller(self)

        self.win = MainWindow(self, config)
        self.win.set_default_size(550, 650)
        self.win.set_title("Tux Katana")
        self.win.set_resizable(True)

        css_provider = Gtk.CssProvider()
        css_provider.load_from_path("style.css")

        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        #display = Gdk.Display.get_default()
        #monitor = display.get_primary_monitor()
        #geometry = monitor.get_geometry()

        #x = (geometry.width - 600) // 2
        #y = (geometry.height - 650) // 2
        self.win.present()
        #self.move(x, y)
    def do_shutdown(self):
        #self.ctrl.port.close()
        close(self)
        Gtk.Application.do_shutdown(self)
        #super().do_shutdown(self)

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--debug", action="store_true", \
            help="Debug Mode on")

    parser.add_argument("-s", "--sysex", action="store_true", \
            help="Log SysEx messages")
    args, gtk_args = parser.parse_known_args()
    args = parser.parse_args()
    log_level = logging.DEBUG if args.debug else logging.INFO
    log_level = log.SYSEX if args.sysex else log_level
    log.setLevel(log_level)

    app = TuxKatana(debug=args.debug)
    try:
        app.run(gtk_args)#sys.argv)
    except KeyboardInterrupt:
        log.info("ctrl+c")
        close()

if __name__ == "__main__":
    main()

