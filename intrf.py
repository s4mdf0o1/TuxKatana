#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk
import mido
from threading import Thread
import sys
import yaml
#import controller

#class Controller:
#    def __init__(self):

class CommandCombo(Gtk.ComboBoxText):
    def __init__(self, items=None):
        super().__init__()
        #self.set_vexpand(False)
        self.entries = items
        print(items)
        if items:
            for item in items:
                self.append_text(item)
        self.connect("changed", self.on_changed)


    def on_changed(self, combo):
        text = combo.get_active_text()
        if text is not None:
            print(f"Sélection: {text}", f"value: {self.entries[text]}")

class LogBox(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        self.append(scrolled)

        self.textview = Gtk.TextView()
        self.textview.set_editable(False)
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        scrolled.set_child(self.textview)

        self.buffer = self.textview.get_buffer()

    def print(self, text):
        end_iter = self.buffer.get_end_iter()
        self.buffer.insert(end_iter, text + "\n")

        # Faire défiler vers le bas
        mark = self.buffer.create_mark(None, self.buffer.get_end_iter(), False)
        self.textview.scroll_to_mark(mark, 0.0, True, 0.0, 1.0)

class AddrEntry(Gtk.Box):
    def __init__(self, name, value, parent):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.parent = parent
        self.name = name
        label = Gtk.Label(label=name+": ")
        self.append(label)

        entry = Gtk.Entry()
        txt = [hex(v).split('x')[1] for v in value]
        txt = ["0"+t if len(t)<2 else t for t in txt]
        self.value = txt
        #entry.set_placeholder_text( " ".join(txt) )
        entry.set_text( " ".join(txt) )
        self.append(entry)
        entry.connect("notify::has-focus", self.parse)
        #self.pack_start(entry, False, False, 0)

    def parse( self, entry, param_boolean ):
        if not entry.has_focus():
            text = entry.get_text().strip()
            try:
                value = [int(x, 16) for x in text.split()]
                if value != self.value:
                    self.parent.logbox.print(f"{self.name}: {[hex(v) for v in value]}")
                    self.value = value

            except ValueError as e:
                print("Erreur de saisie :", e)
            return False  # False = laisse GTK gérer aussi l'événement
        

class MainWindow(Gtk.Window):
    def __init__(self, app):
        super().__init__(application=app)
        #self.set_default_size(400, 200)
        v_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_child(v_box)
        h_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.command = CommandCombo(app.params["Command"])
        self.command.set_active(0)
        entries_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        v_box.append(h_box)
        h_box.append(entries_box)
        h_box.append(self.command)
        self.entries={}
        for p in app.params:
            if type(app.params[p]) == list:
                self.entries[p] = AddrEntry(p, app.params[p], self)
                entries_box.append(self.entries[p])

        #self.vendor = AddrEntry("Vendor",1, self)
        #self.device = AddrEntry("Device",1, self)
        #self.model  = AddrEntry("Model", 4, self)
        #entries_box.append(self.vendor)
        #entries_box.append(self.device)
        #entries_box.append(self.model)
        self.logbox = LogBox()
        v_box.append(self.logbox)

class KatanaDebug(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.domosys.KatanaDebug")
        with open("params/params.yaml", 'r') as f:
            self.params = yaml.safe_load(f)
        #self.controller = controller.KatanaController()

    def do_activate(self):
        win = MainWindow(self)
        win.set_title("Katana Debug")
        #win.set_default_size(800,600)
        win.set_resizable(True)
        #win.maximize()

        #css_provider = Gtk.CssProvider()
        #css_provider.load_from_path("style.css")

        #Gtk.StyleContext.add_provider_for_display(
        #    Gdk.Display.get_default(),
        #    css_provider,
        #    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        #)

        win.present()

if __name__ == "__main__":
    app = KatanaDebug()
    sys.exit(app.run(sys.argv))


