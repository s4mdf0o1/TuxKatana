import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk#, GLib, Gdk

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


