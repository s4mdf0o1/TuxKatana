import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio #GLib, Gdk, GObject
import os

class FileChooser(Gtk.FileChooserDialog):
    def __init__(self, win, parent, title="Choose Preset file",
                 action=Gtk.FileChooserAction.OPEN):#,
                 #accept_label="Ouvrir", cancel_label="Annuler"):
        self.parent= parent
        super().__init__(title=title, transient_for=win, action=action)
                         #accept_label=accept_label,
                         #cancel_label=cancel_label)

        self.set_modal(True)
        cwd = os.getcwd()
        self.set_current_folder(Gio.File.new_for_path(cwd+"/presets"))

    def add_filter(self, name, patterns):
        f = Gtk.FileFilter()
        f.set_name(name)
        for p in patterns:
            f.add_pattern(p)
        Gtk.FileChooserNative.add_filter(self, f)
        #self.add_filter(f)

    def choose(self):
        def on_response(dialog, response):
            file_path = None
            if response == Gtk.ResponseType.ACCEPT:
                file = dialog.get_file()
                if file:
                    file_path = file.get_path()
                    dialog.parent.file_path = file_path
                    dialog.parent.file.set_text(os.path.basename(file_path).split('.')[0])
            dialog.destroy()

        self.connect("response", on_response)
        self.show()
 
