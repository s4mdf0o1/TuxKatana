#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk
import mido
from threading import Thread
import sys

class MainWindow(Gtk.Window):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_default_size(400, 200)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_child(box)

        # Slider Bass
        self.bass_slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 127, 1)
        self.bass_slider.connect("value-changed", self.on_bass_changed)
        box.append(self.bass_slider)

        # Thread pour recevoir les messages MIDI
        Thread(target=self.listen_midi, daemon=True).start()

    def on_bass_changed(self, slider):
        value = int(slider.get_value())
        print("Bass changed:", value)
        # Ici : envoi MIDI CC vers Katana

    def listen_midi(self):
        inport = mido.open_input("KATANA:KATANA MIDI 1 28:0")
        for msg in inport:
            if msg.type == 'control_change' and msg.control == 20:  # Bass
                # Mettre à jour slider dans le thread principal
                GLib.idle_add(self.bass_slider.set_value, msg.value)

class TuxKatana(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.domosys.TuxKatana")

    def do_activate(self):
        win = MainWindow(self)
        win.set_title("Tux Katana")
        win.set_default_size(800,600)
        win.set_resizable(True)
        #win.maximize()

        css_provider = Gtk.CssProvider()
        css_provider.load_from_path("style.css")

        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        win.present()


if __name__ == "__main__":
    app = TuxKatana()
    sys.exit(app.run(sys.argv))


