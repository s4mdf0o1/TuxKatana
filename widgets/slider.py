import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GObject

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
        self.scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, \
                adjustment=adjustment)
        self.scale.set_digits(0)
        self.scale.set_draw_value(True)
        self.scale.set_value_pos(Gtk.PositionType.RIGHT)
        self.scale.set_hexpand(True)
        self.scale.name = ""
        label = Gtk.Label(label=name)
        label.set_size_request(80, -1)
        self.append(label)
        self.append(self.scale)

    @GObject.Property(type=float, default=0.0)
    def value(self):
        return self.scale.get_value()

    @value.setter
    def value(self, val):
        self.scale.set_value(val)

    @GObject.Property(type=str, default="")
    def name(self):
        return self.scale.name

    @name.setter
    def name(self, val):
        self.scale.name = val

    def connect(self, name, *args, **kwargs):
        return self.scale.connect(name, *args, **kwargs)
