import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio #GLib, Gdk, GObject
import os

from .file_chooser import FileChooser
from .channel_chooser import ChannelChooser

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

class PresetUI(Gtk.Box):
    def __init__(self, own_ctrl):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.own_ctrl = own_ctrl
        self.filename = None
        self.file_path = None
        self.selected_channel = None

        h_box1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        label = Gtk.Label(label="Filename: ")
        h_box1.append(label)
        self.file = Gtk.Entry()
        h_box1.append(self.file)
        ext = Gtk.Label(label=".tsl")
        h_box1.append(ext)
        writechan = Gtk.Button(label="Write to Amp")
        writechan.connect("clicked", self.on_load_clicked)
        h_box1.append(writechan)
        self.append(h_box1)

        selectfile = Gtk.Button(label="Select TSL file")
        selectfile.connect("clicked", self.on_select_clicked)
        self.append(selectfile)

        savefile = Gtk.Button(label="Save TSL file")
        savefile.connect("clicked", self.on_save_clicked)
        self.append(savefile)


    def on_select_clicked(self, widget):
        win = self.own_ctrl.device.ctrl.parent.win
        chooser = FileChooser(win, parent=self, title="Open .tsl file")
        chooser.add_filter("TSL Files", ["*.tsl"])
        chooser.add_buttons(
            "_Cancel", Gtk.ResponseType.CANCEL,
            "_Open", Gtk.ResponseType.ACCEPT
        )
        file_path = chooser.choose()
        log.debug(file_path)
        if self.file_path:
            self.filename = os.path.basename(self.file_path).split('.')[0]
            self.file.set_text(self.filename)

    def on_load_clicked(self, button):
        win = self.own_ctrl.device.ctrl.parent.win
        win.set_sensitive(False)
        ch_chooser = ChannelChooser(win, self)
        ch_chooser.connect("response", self.on_channel_choosed)
        ch_chooser.show()

    def on_channel_choosed(self, dialog, response):
        win = self.own_ctrl.device.ctrl.parent.win
        win.set_sensitive(True)
        if response == Gtk.ResponseType.OK:
            self.selected_channel = dialog.get_selected_channel()
            print("Choosed Channel :", self.selected_channel)
        else:
            print("Canceled")
        dialog.destroy()

    def on_save_clicked(self, button):
        #log.debug(f"{self.dest_dir+self.file_path}")
        filename = self.file.get_text()
        log.debug(filename)
        self.own_ctrl.save(filename + '.tsl')
