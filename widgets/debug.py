import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from ruamel.yaml import YAML
yaml = YAML(typ="safe")
config = ""
with open("params/config.yaml", "r") as f:
    config = yaml.load(f)
dots = config['DOTS']

from lib.midi_bytes import Address, MIDIBytes

class Debug(Gtk.Box):
    def __init__(self, ctrl):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.ctrl = ctrl

        self.midi = Gtk.ComboBoxText()
        self.midi.append_text("SysEx")
        self.midi.append_text("Program_Change")
        self.midi.append_text("Control_Change")
        self.midi.set_active(0)

        self.cmd = Gtk.ComboBoxText()
        self.cmd.append_text("GET")
        self.cmd.append_text("SET")
        self.cmd.set_active(0)
        
        h_box1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        label = Gtk.Label(label="Adresse: ")
        h_box1.append(label)
        self.address = Gtk.Entry()
        h_box1.append(self.address)

        h_box2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        label = Gtk.Label(label="Valeur: ")
        h_box2.append(label)
        self.value = Gtk.Entry()
        h_box2.append(self.value)

        h_bbut = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        but_send_amp = Gtk.Button(label="SEND to AMP")
        but_send_amp.connect("clicked", self.send)
        h_bbut.append(but_send_amp)

        but_read_mry = Gtk.Button(label="READ Memory")
        but_read_mry.connect("clicked", self.read_memory)
        h_bbut.append(but_read_mry)

        but_save_mry = Gtk.Button(label="Save Mry to File")
        but_save_mry.connect("clicked", self.save_mry)

        h_box3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        label = Gtk.Label(label="Log Note: ")
        h_box3.append(label)
        self.log_note = Gtk.Entry()
        h_box3.append(self.log_note)
        but_log = Gtk.Button(label="ADD Note")
        but_log.connect("clicked", self.add_log_note)
        h_box3.append(but_log)

        h_box4 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        label = Gtk.Label(label="Log File: ")
        h_box4.append(label)
        self.log_file = Gtk.Entry()
        h_box4.append(self.log_file)
        but_store = Gtk.Button(label="Store LOG")
        but_store.connect("clicked", self.store_log)
        h_box4.append(but_store)

        self.append(self.midi)
        self.append(self.cmd)
        self.append(h_box1)
        self.append(h_box2)
        self.append(h_bbut)
        self.append(but_save_mry)
        self.append(h_box3)
        self.append(h_box4)

    def test(self, but):
        self.ctrl.device.amplifier.amp_type = 12

    def add_log_note(self, button):
        note = self.log_note.get_text()
        log_sysex.info(note)

    def store_log(self, button):
        filename = self.log_file.get_text()
        archived = rotate_log(filename)
        log.info(f"Archived: {archived}")

    def send(self, button, cmd=None, addr=None, val=None):
        mode = self.midi.get_active_text()
        if mode == "SysEx":
            cmd = self.cmd.get_active_text()
            cmd = True if cmd == 'SET' else False
            Addr = Address( self.address.get_text() )
            Data = MIDIBytes( self.value.get_text() )
            self.ctrl.send( Addr, Data, cmd )
        elif mode == "Program_Change":
            program = int(self.address.get_text())
            self.ctrl.pc.program = program
            self.ctrl.port.send(self.ctrl.pc)
        elif mode == "Control_Change":
            address = int(self.address.get_text())
            value = int(self.value.get_text())
            self.ctrl.cc.control = address
            self.ctrl.cc.value = value
            self.ctrl.port.send(self.ctrl.cc)

    def read_memory(self, button):
        Addr = Address(self.address.get_text())
        size = int(self.value.get_text())
        value = self.ctrl.device.mry.read(Addr, size, True)
        self.value.set_text(value)

    def save_mry(self, filename="mry_dump.bin"):
        self.ctrl.device.mry.save_to_file()
