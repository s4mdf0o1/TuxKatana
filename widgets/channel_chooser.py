import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk#, GLib, Gdk

class ChannelChooser(Gtk.Dialog):
    def __init__(self, win, parent):
        super().__init__(title="Choose Channel", transient_for=win, modal=True)
        self.set_default_size(300, 200)
        self.set_decorated(False)
        self.add_buttons(
            "_Cancel", Gtk.ResponseType.CANCEL,
            "_OK", Gtk.ResponseType.OK
        )
        box = self.get_content_area()
        box.get_style_context().add_class("bordered")
        label = Gtk.Label(label="Choose Channel to load Preset to: ")
        self.channels = Gtk.ComboBoxText()
        for i in range(8):
            text = 'CH_' + str(i+1)
            self.channels.append_text(text)

        box.append(label)
        box.append(self.channels)

    def get_selected_channel(self):
        return self.channels.get_active()+1


