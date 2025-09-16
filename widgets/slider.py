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
        #AntiFlood.__init__(self)
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
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
        #self.scale.name = ""
        label = Gtk.Label(label=name)
        label.set_size_request(80, -1)
        self.append(label)
        self.append(self.scale)
        self.get_style_context().add_class('slider')
        
        if own_ctrl:
            own_ctrl.bind_property(
                bind_prop, self, "value",\
                GObject.BindingFlags.SYNC_CREATE )#|\
                #GObject.BindingFlags.BIDIRECTIONAL )
        self.scale.connect("value-changed", self._on_scale_changed)

    def _on_scale_changed(self, scale):
        val = scale.get_value()
        self.set_property("value", val)   # met à jour la propriété GObject
        self.schedule_value(val)          # déclenche l’anti-flood

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

    #def connect(self, name, *args, **kwargs):
    #    return self.scale.connect(name, *args, **kwargs)

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
            return str(100 - v)
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
            #if time < 1.0:
            time = int(round(time))
            #log.debug(time)
            if time < 1000:
                return self.vals['unit'].format(time=time)
            else:
                # log.debug(f"{self.format_name} {time=}")
                return self.vals['kilo'].format(time=time/1000)
        elif 'gain' in self.format_name:
            gain = self.vals['vmax'] - v
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

#        if valmin in vals:
#            self.valmin = vals['valmin']
#        if valmax in vals:
#            self.valmax = vals['valmax']
#
#
#        #fmt = self.format[format_name]
#        #self.scale.set_lower(fmt['vmin'])
#        #self.scale.set_upper(fmt['vmax'])
#        format_func = getattr(self, "format_"+format_name)
#        self.scale.set_format_value_func(format_func)
#
#    def format_high_freq(self, scale, v):
#        return self.format_freq(scale, v, 630, 12500, 0x0e)
#    def format_freq(self, scale, v, f_min, f_max, upper):
#        adj = scale.get_adjustment()
#        v_min = int(adj.get_lower())
#        v_max = int(adj.get_upper())
#        freq = f_min * ((f_max / f_min) ** (v / upper))
#        if freq >= 1000:
#            return f"{freq/1000:.1f} kHz"
#        else:
#            return f"{int(freq)} Hz"
#
#    def format_t_time(self, scale, v):
#        return self.format_time(scale, v, 1000)
#    def format_time(self, scale, v, div=1):
#        adj = scale.get_adjustment()
#        v_min = int(adj.get_lower())
#        v_max = int(adj.get_upper())
#        if div > 1:
#            v /= div
#        if v < 1.0:
#            return f"{int(round(v*1000))} ms"
#        else:
#            return f"{v:.2f} s"
#
#    def format_percent(self, scale, v):
#        return f"{v:.2f} %"

