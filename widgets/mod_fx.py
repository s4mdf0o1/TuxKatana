import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

import importlib

from .slider import Slider
from .tabbed_panel import TabbedPanel
from .bank import Bank
from .toggle import Toggle
from .box_inner import BoxInner
from .combo_store import ComboStore
from lib.effect import Effect

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from lib.midi_bytes import Address, MIDIBytes

from lib.set_mapping import add_properties

class ModFx(Effect, Gtk.Box):
    def __init__(self, ctrl):
        super().__init__(ctrl, self.mapping)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(6)
        self.ctrl = ctrl

        # log.debug(self.name)
        banks = {"GREEN":'1', "RED":'2', "YELLOW":'3'}
        self.bank_select = Bank(self.name, banks)
        self.bank_select.buttons[0].set_status_id(1)
        self.bank_select.buttons[2].set_status_id(3)
        self.append(self.bank_select)
        
        self.bind_property(
            self.prefix + "bank_sel", self.bank_select, "selected",
            GObject.BindingFlags.BIDIRECTIONAL |\
            GObject.BindingFlags.SYNC_CREATE )

        box_sel = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        self.types_list = ComboStore( self, self.types, self.prefix + "type_idx")
        box_sel.append(self.types_list)

        self.vol_lvl = Slider( "Volume", "normal", self, self.prefix+"vol_lvl" )
        box_sel.append(self.vol_lvl)
        self.append(box_sel)

        self.stack = Gtk.Stack()
        # self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.append(self.stack)

        self.load_modfx()

        self.connect(f"notify::{self.prefix.replace('_','-')}type-idx", self.on_type_changed)

    def on_type_changed(self, obj, pspec):
        idx = self.get_property(self.prefix + 'type_idx')
        children = self.get_stack_children(self.stack)
        if 0 <= idx < len(children):
            self.stack.set_visible_child(children[idx])
        else:
            log.debug("Not implemented")

    def get_stack_children(self, stack: Gtk.Stack):
        children = []
        child = stack.get_first_child()
        while child:
            children.append(child)
            child = child.get_next_sibling()
        return children

    def load_modfx(self):
        log.info(f"Loading {self.name} Effects...")
        i = 0
        for name, code in self.types.items():
            # log.debug(name)
            exists = any(row[1] == name for row in self.types_list.store)
            if not exists:
                self.types_list.store.append([i,name, code])
            i += 1
            box = self.make_ui(name)
            if box:
                log.info(f"Loading: -{name}-")
                # log.debug(box.parent_prefix)
                self.stack.add_named(box, name)

    def on_bank_changed(self, obj, pspec):
        idx = getattr(obj, pspec.name.replace("-", "_"))
        children = self.get_stack_children(self.stack)
        # log.debug(f"{idx=} {children.__class__.__name__}") 
        if 0 <= idx < len(children):
            self.stack.set_visible_child(children[idx])
        else:
            log.debug(f"Not implemented")

    def make_ui(self, name):
        filename = name.lower().replace(" ", "_")
        ui_name = "".join(w.capitalize() for w in name.split())
        # log.debug(f"{name} {filename} {lib_name} {ui_name}")
        try:
            ui = importlib.import_module("widgets.modfx."+filename)
            ui_cls = getattr(ui, ui_name)
            # log.debug(ui_cls)
        except (ModuleNotFoundError, AttributeError) as e:
            log.warning(f"widgets.modfx.{filename}.{ui_name}' not found {e}")
            return None
        ui_obj = ui_cls(self.ctrl, self.prefix)
        return ui_obj

@add_properties()
class Mod(ModFx, Gtk.Box):
    mod_sw       = GObject.Property(type=bool, default=False)
    mo_type     = GObject.Property(type=str)
    mo_type_idx  = GObject.Property(type=int, default=0)
    mo_type_G   = GObject.Property(type=str)
    mo_type_R   = GObject.Property(type=str)
    mo_type_Y   = GObject.Property(type=str)
    mo_bank_sel = GObject.Property(type=int, default=0)
    mo_return   = GObject.Property(type=int, default=0)
    mo_status   = GObject.Property(type=int, default=0)
    mo_vol_lvl  = GObject.Property(type=int, default=0)
    def __init__(self, ctrl):
        super().__init__(ctrl)

@add_properties()
class Fx(ModFx, Gtk.Box):
    fx_sw       = GObject.Property(type=bool, default=False)
    fx_type     = GObject.Property(type=str)
    fx_type_idx  = GObject.Property(type=int, default=0)
    fx_type_G   = GObject.Property(type=str)
    fx_type_R   = GObject.Property(type=str)
    fx_type_Y   = GObject.Property(type=str)
    fx_bank_sel = GObject.Property(type=int, default=0)
    fx_return   = GObject.Property(type=int, default=0)
    fx_status   = GObject.Property(type=int, default=0)
    fx_vol_lvl  = GObject.Property(type=int, default=0)
    def __init__(self, ctrl):
        super().__init__(ctrl)
 
