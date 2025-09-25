import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GObject

from lib.anti_flood import AntiFlood

from ruamel.yaml import YAML
yaml = YAML(typ="rt")

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

class Slider(AntiFlood, Gtk.Box):
    __gsignals__ = {
        "delayed-value": (GObject.SignalFlags.RUN_LAST, None, (float,))
    }

    def __init__(self, name, format_name="normal", own_ctrl=None, bind_prop=""):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        self.format_name = format_name
        adjustment = Gtk.Adjustment(
            lower=0,
            upper=100,
            step_increment=1,
            page_increment=8
        )
        self.scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, \
                adjustment=adjustment)
        self.scale.set_digits(0)
        self.scale.set_draw_value(True)
        self.scale.set_value_pos(Gtk.PositionType.RIGHT)
        self.scale.set_hexpand(True)
        self.set_format()
        label = Gtk.Label(label=name)
        label.set_size_request(80, -1)
        label.set_hexpand(False)
        self.append(label)
        self.append(self.scale)
        self.get_style_context().add_class('slider')
        
        if bind_prop:
            self.name = bind_prop
        
        if own_ctrl:
            self.own_ctrl = own_ctrl
            # log.debug(f"{bind_prop}")
            own_ctrl.bind_property(
                bind_prop, self, "value",\
                GObject.BindingFlags.SYNC_CREATE )
            self.connect("delayed-value", self.on_slider_changed)
        self.scale.connect("value-changed", self._on_scale_changed)

    def on_slider_changed( self, slider, value):
        old_val = self.own_ctrl.get_property(slider.name)
        value = int(value)
        # log.debug(f"{old_val} {value}")
        if value != old_val:
            self.own_ctrl.set_property(slider.name, int(value))

    def _on_scale_changed(self, scale):
        val = scale.get_value()
        self.set_property("value", val)
        self.schedule_value(val)          # start AntiFlood

    @GObject.Property(type=float, default=0.0)
    def value(self):
        return int(self.scale.get_value())

    @value.setter
    def value(self, val):
        self.scale.set_value(float(val))

    @GObject.Property(type=str, default="")
    def name(self):
        return self.scale.name

    @name.setter
    def name(self, val):
        self.scale.name = val

    def set_format(self):
        vals = {}
        with open("params/slider_formats.yaml", "r") as f:
            vals = yaml.load(f)
        self.vals = vals[self.format_name]
        adj = self.scale.get_adjustment()
        adj.set_lower(self.vals['vmin'])
        adj.set_upper(self.vals['vmax'])
        self.scale.set_format_value_func(self.format_scale)

    def format_scale(self, scale, v):
        if self.format_name in ['normal', 'pattern', 'density']:
            return str(v)
        if self.format_name == 'plus_minus':
            return str(v - 50)
        if self.format_name == 'percent':
            return self.vals['unit'].format(percent=v)
        if 'freq' in self.format_name:
            f_min = self.vals['valmin']
            f_max = self.vals['valmax']
            v_max = self.vals['vmax']
            if f_min ==0:
                f_min = 1
            freq = freq = f_min * ((f_max / f_min) ** (v / v_max))
            freq = int(round(freq))
            if freq < 1000:
                return self.vals['unit'].format(freq=freq)
            else:
                return self.vals['kilo'].format(freq=freq/1000)
        elif 'time' in self.format_name:
            x1, x2 = self.vals['vmin'], self.vals['vmax']
            y1, y2 = self.vals['valmin'], self.vals['valmax']
            a = (y2 - y1) / (x2 - x1)
            b = y1 - a * x1
            time = a * v + b
            time = int(round(time))
            #log.debug(time)
            if time < 1000:
                return self.vals['unit'].format(time=time)
            else:
                # log.debug(f"{self.format_name} {time=}")
                return self.vals['kilo'].format(time=time/1000)
        elif 'gain' in self.format_name:
            gain = v - 20 #self.vals['vmax']
            return self.vals['unit'].format(gain=gain)
        elif self.format_name == 'mid_q':
            return str(0.5 * (2 ** v))
        elif self.format_name == 'repeat':
            x1, x2 = self.vals['vmin'], self.vals['vmax']
            y1, y2 = self.vals['valmin'], self.vals['valmax']
            a = (y2 - y1) / (x2 - x1)
            b = y1 - a * x1
            repeat = a * v + b
            return self.vals['unit'].format(repeat=repeat)


