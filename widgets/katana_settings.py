import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk
import mido

from ruamel.yaml import YAML
yaml = YAML(typ="safe")
config = ""
with open("params/config.yaml", "r") as f:
    config = yaml.load(f)
dots = config['DOTS']

from .katana_debug import KatanaDebug
from .presets import Presets

class KS_TabbedPanel(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        self.stack = Gtk.Stack()
        self.stack.set_transition_duration(150)

        sidebar = Gtk.StackSidebar()
        sidebar.set_stack( self.stack )
        self.set_vexpand(True)

        self.append(sidebar)
        self.append(self.stack)

    def add_tab(self, widget, name, title):
        self.stack.add_titled(widget, name, title)

    def set_active_tab(self, name):
        self.stack.set_visible_child_name(name)

class KS_Slider(Gtk.Box):
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
        self.scale.connect("value-changed", self.on_value_changed)
        label = Gtk.Label(label=name)
        self.append(label)
        self.append(self.scale)

    def on_value_changed(self, slider):
        value = int(slider.get_value())
        print(f"Valeur sélectionnée: {value}")

    # Méthode pratique
    def get_int_value(self):
        return int(self.scale.get_value())

class KS_Settings(Gtk.Box):
    def __init__(self, name, cfg, ctrl):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.ctrl = ctrl
        if name == "DEBUG":
            debug = KatanaDebug(ctrl)
            self.append(debug)
        else:
            self.slider = KS_Slider( "Level", 50)
            self.append(self.slider)

class KatanaSettings(Gtk.Box):
    def __init__(self, label, cfg, ctrl):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.get_style_context().add_class("inner")
        self.ctrl = ctrl
        self.title = Gtk.Label(label=label)
        self.append(self.title)
        #box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        tabs = KS_TabbedPanel()
        for name in ["PRESETS","AMP", "BOOSTER", "MOD", "FX", "DELAY", "REVERB", "CHAIN", "DEBUG"]:
            page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            tabs.add_tab(page, name.lower(), name)
            if name == "PRESETS":
                self.presets = Presets(ctrl)
                page.append(self.presets)
            else:
                ks_settings = KS_Settings( name, config, ctrl)
                page.append(ks_settings)

        #page1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        #tabs.add_tab(page1, "tab1", "BOOSTER")

        #page2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        #page2.append(Gtk.Label(label="Contenu de l’onglet 2"))
        #tabs.add_tab(page2, "tab2", "MOB")

        tabs.set_active_tab("debug")
        #box.append(tabs)
        self.append(tabs)
        
        #self.booster = KS_Slider( "Level", 50)
        #Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 127, 1)
        #self.bass_slider.connect("value-changed", self.on_bass_changed)
        #page1.append(self.booster)


