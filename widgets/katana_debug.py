import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk

import logging
from lib.log_setup import LOGGER_NAME, rotate_log
log_sysex = logging.getLogger(LOGGER_NAME)
dbg=logging.getLogger("debug")

from ruamel.yaml import YAML
yaml = YAML(typ="safe")
config = ""
with open("params/config.yaml", "r") as f:
    config = yaml.load(f)
dots = config['DOTS']

class KatanaDebug(Gtk.Box):
    def __init__(self, ctrl):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.ctrl = ctrl

        self.edit = Gtk.ToggleButton(label="Edit Mode")
        self.edit.connect("toggled", self.switch_mode)
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

        but_send = Gtk.Button(label="SEND")
        but_send.connect("clicked", self.send)

        but_cfg = Gtk.Button(label="Get_Config")
        but_cfg.connect("clicked", self.set_config)

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
        self.append(self.edit)
        self.append(self.cmd)
        self.append(h_box1)
        self.append(h_box2)
        self.append(but_send)
        self.append(but_cfg)
        self.append(h_box3)
        self.append(h_box4)

    def add_log_note(self, button):
        note = self.log_note.get_text()
        log_sysex.info(note)

    def store_log(self, button):
        filename = self.log_file.get_text()
        archived = rotate_log(filename)
        dbg.info(f"Archived: {archived}")

    def switch_mode( self, button ):
        header = self.ctrl.message.header
        self.midi.set_active(0)
        if button.get_active():
            self.send(None, 'SET', '7F 00 00 01', '01')
        else:
            self.send(None, 'SET', '7F 00 00 01', '00')

    def send(self, button, cmd=None, addr=None, val=None):
        mode = self.midi.get_active_text()
        msg_obj = self.ctrl.message
        from_str = msg_obj.addrs.from_str
        if mode == "SysEx":
            header = msg_obj.header
            if not cmd:
	            cmd = msg_obj.addrs[self.cmd.get_active_text()]
            else:
	            cmd = msg_obj.addrs[cmd]
            if not addr and not val:
	            addr = from_str( self.address.get_text() )
	            val = from_str( self.value.get_text() )
            else:
	            addr = from_str( addr )
	            val = from_str( val )
	
	        #msg = [int(v, 16) for v in txt.split(' ')]
            cks = msg_obj.checksum(addr + val)
            data = header + cmd + addr + val + [cks]
            self.ctrl.sysex.data = data
            self.ctrl.send(self.ctrl.sysex, self.debug_msg)
        elif mode == "Program_Change":
            program = int(self.address.get_text())
            self.ctrl.pc.program = program
            self.ctrl.port.send(self.ctrl.pc)
        elif mode == "Control_Change":
            #dbg.debug("Control")
            address = int(self.address.get_text())
            value = int(self.value.get_text())
            self.ctrl.cc.control = address
            self.ctrl.cc.value = value
            self.ctrl.port.send(self.ctrl.cc)

    def debug_msg(self, msg):
        #self.ctrl.listener_callback = None
        dbg.debug(f"debug_msg: {msg.hex()}")

    def set_config(self, button):
        self.cmd.set_active(0)
        self.address.set_text('60 00 00 00')
        self.value.set_text('00 00 0f 48')
