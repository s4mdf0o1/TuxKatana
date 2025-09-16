import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio #GLib, Gdk, GObject
import os

from .file_chooser import FileChooser

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

class PresetUI(Gtk.Box):
    def __init__(self, own_ctrl):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.own_ctrl = own_ctrl
        self.file_path = None

        h_box1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        label = Gtk.Label(label="Filename: ")
        h_box1.append(label)
        self.file = Gtk.Entry()
        h_box1.append(self.file)
        ext = Gtk.Label(label=".tsl")
        h_box1.append(ext)

        self.append(h_box1)
        button = Gtk.Button(label="Open Preset file")
        button.connect("clicked", self.on_button_clicked)
        self.append(button)

    def on_button_clicked(self, widget):
        win=self.own_ctrl.device.ctrl.parent.win
        chooser = FileChooser(win, parent=self, title="Ouvrir un fichier .tsl")
        chooser.add_filter("Fichiers TSL", ["*.tsl"])
        chooser.add_filter("Tous les fichiers", ["*"])
        chooser.add_buttons(
            "_Annuler", Gtk.ResponseType.CANCEL,
            "_Ouvrir", Gtk.ResponseType.ACCEPT
        )
        file_path = chooser.choose()
        log.debug(file_path)
        if self.file_path:
            #print("Fichier choisi :", file_path)
            self.file.set_text(os.path.basename(self.file_path).split('.')[0])

  
