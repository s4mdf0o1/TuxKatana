import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk#, GLib, Gdk, GObject

class Slider(Gtk.Box):
    def __init__(self, name, value=0):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        adjustment = Gtk.Adjustment(
            value=value,
            lower=0,
            upper=127,
            step_increment=1,
            page_increment=8
        )
        self.scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment)
        self.scale.set_digits(0)
        self.scale.set_draw_value(True)
        self.scale.set_value_pos(Gtk.PositionType.RIGHT)
        self.scale.set_hexpand(True)
        #self.scale.connect("value-changed", self.on_value_changed)
        label = Gtk.Label(label=name)
        self.append(label)
        self.append(self.scale)

    def on_value_changed(self, slider):
        dbg.debug(f"KS_Slider.on_value_changed:")
        value = int(slider.get_value())
        print(f"Valeur sélectionnée: {value}")

    # Méthode pratique
    def get_int_value(self):
        return int(self.scale.get_value())

