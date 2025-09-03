import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk

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

        button = Gtk.Button(label="SEND")
        button.connect("clicked", self.send)

        self.append(self.midi)
        self.append(self.edit)
        self.append(self.cmd)
        self.append(h_box1)
        self.append(h_box2)
        self.append(button)

    def switch_mode( self, button ):
        header = self.ctrl.message.header
        if button.get_active():

            print("active")
        else:
            print("inactive")

    def send(self, button):
        header = self.ctrl.message.header
        cmd = self.ctrl.message.addrs[self.cmd.get_active_text()]
        addr = [int(v, 16) for v in self.address.get_text().split(' ')]
        val = [int(v, 16) for v in self.value.get_text().split(' ')]

        #msg = [int(v, 16) for v in txt.split(' ')]
        cks = self.ctrl.message.checksum(addr + val)
        data = header + cmd + addr + val + [cks]
        #dbg = self.ctrl.message.addrs.to_str(data)
        #print(f"{dbg=}")
        self.ctrl.sysex.data = data
        self.ctrl.send(self.ctrl.sysex, self.debug_msg)

    def debug_msg(self, msg):
        #self.ctrl.listener_callback = None
        print(f"debug_msg: {msg.hex()}")
