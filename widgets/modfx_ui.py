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

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

class ModFxUI(Gtk.Box):
    def __init__(self, ctrl, own_ctrl, name):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.ctrl = ctrl
        self.name = name
        self.own_ctrl = own_ctrl
        self.prefix = own_ctrl.prefix
        self.stack = Gtk.Stack()
        # self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
 
        banks = {"GREEN":'1', "RED":'2', "YELLOW":'3'}
        self.bank_select = Bank(name, banks)
        # log.debug(f"bank:{name}")
        self.bank_select.buttons[0].set_status_id(1)
        self.bank_select.buttons[2].set_status_id(3)
        self.append(self.bank_select)
        
        self.own_ctrl.bind_property(
            self.prefix + "bank_sel", self.bank_select, "selected",
            GObject.BindingFlags.BIDIRECTIONAL |\
            GObject.BindingFlags.SYNC_CREATE )

        box_sel = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)

        self.types = ComboStore( own_ctrl, 'Types')
        box_sel.append(self.types)
        self.append(box_sel)

        self.vol_lvl = Slider( "Volume", "normal", self.own_ctrl, self.prefix+"vol_lvl" )
        box_sel.append(self.vol_lvl)

        self.append(self.stack)

        for bank in ['-G', '-R', '-Y']:
            # log.debug("notify::"+self.prefix+"_bank"+bank)
            self.own_ctrl.connect(
                    "notify::"+self.prefix.replace('_','-')+"bank"+bank,
                    self.on_bank_changed
                )

        self.own_ctrl.connect("notify::type-idx", self.on_type_changed)
        self.own_ctrl.connect("modfx-map-ready", self.on_modfx_loaded)

    def on_type_changed(self, obj, pspec):
        idx = self.own_ctrl.type_idx
        children = self.get_stack_children(self.stack)
        # log.debug(f"{idx} {children}")
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

    def on_bank_changed(self, obj, pspec):
        idx = getattr(obj, pspec.name.replace("-", "_"))
        children = self.get_stack_children(self.stack)
        # log.debug(f"{idx=} {children.__class__.__name__}") 
        if 0 <= idx < len(children):
            self.stack.set_visible_child(children[idx])
        else:
            log.debug(f"Not implemented")

    def on_modfx_loaded(self, device, map_types):
        i = 0
        types = map_types['Types']
        for name, code in types.items():
            log.debug(name)
            self.types.store.append([i,name, code])
            i += 1
            box = self.make_ui(name)
            # log.debug(box)
            if box:
                self.stack.add_named(box, name)

    def make_ui(self, name):
        filename = name.lower().replace(" ", "_")
        lib_name = "".join(w.capitalize() for w in name.split())
        ui_name = lib_name + "UI"
        # log.debug(f"{name} {filename} {lib_name} {ui_name}")
        try:
            ui = importlib.import_module("widgets.modfx."+filename)
            ui_cls = getattr(ui, ui_name)
            # log.debug(ui_cls)
        except (ModuleNotFoundError, AttributeError) as e:
            log.warning(f"widgets.modfx.{filename}.{ui_name}' not found {e}")
            return None
        try:
            lib = importlib.import_module("lib.modfx."+filename)
            lib_cls = getattr(lib, lib_name)
            # log.debug(lib_cls)
        except (ModuleNotFoundError, AttributeError) as e:
            log.warning(f"lib.modfx.{filename}.{lib_name}' not found {e}")
            return None
        lib_obj = lib_cls(self.ctrl.device, self.prefix)
        lib_obj.set_mry_map()
        self.own_ctrl.libs[self.prefix+filename] = lib_obj
        # log.debug(self.own_ctrl.libs)
        ui_obj = ui_cls(lib_obj)
        # log.debug(f"{self.name} {ui_obj.__class__.__name__} {lib_obj.prefix=}")
        return ui_obj

