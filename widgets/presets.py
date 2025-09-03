import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk
from time import sleep

DEBUG = True
def debug( txt ):
    if DEBUG:
        print(txt)

class Presets(Gtk.Box):
    def __init__(self, ctrl):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.ctrl = ctrl
        self.cb_presets = Gtk.ComboBoxText()
        
        self.append(self.cb_presets)
        
    def get_presets(self):
        header = self.ctrl.message.header
        cmd = self.ctrl.message.addrs['GET']
        for i in range(1,9):
            addr = self.ctrl.message.addrs['PRESET_'+str(i)]
            val = [0,0,0,0x10]
            cks = self.ctrl.message.checksum(addr + val)
            data = header + cmd + addr + val + [cks]
            self.ctrl.sysex.data = data
            self.ctrl.send(self.ctrl.sysex, self.decode_msg)
            #sleep(.1)


    def decode_msg( self, msg ):
        debug(f"debug_msg: {msg.hex()}")
        data = list(msg.data)
        if data[0:6] == self.ctrl.message.header:
            command = data[6]
            function = data[7:11]
            if command == 0x12 and function[0] == 0x10:
                preset_txt = ''.join([chr(v) for v in data[11:27]])
                self.cb_presets.append_text(preset_txt)

       

