import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

from .slider import Slider
from .tabbed_panel import TabbedPanel
from .bank import Bank
from .toggle import Toggle
import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)
from lib.tools import from_str, midi_str_to_int

class DelayUI(Gtk.Box):
    def __init__(self, own_ctrl):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        #self.ctrl = ctrl
        #self.own_ctrl = self.ctrl.device.delay
        self.own_ctrl = own_ctrl
        
        banks = {"GREEN":'1', "RED":'2', "YELLOW":'3'}
        self.bank_select = Bank("REVERB", banks)
        self.bank_select.buttons[0].set_status_id(1)
        self.bank_select.buttons[2].set_status_id(3)
        self.append(self.bank_select)

        self.own_ctrl.bind_property(
            "bank_select", self.bank_select, "selected",
            GObject.BindingFlags.BIDIRECTIONAL |\
            GObject.BindingFlags.SYNC_CREATE )

        box_sel = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        self.types_store = Gtk.ListStore(int, str, str)
        self.types = Gtk.ComboBox.new_with_model(self.types_store)
        self.types.set_hexpand(True)
        renderer = Gtk.CellRendererText()
        self.types.pack_start(renderer, True)
        self.types.add_attribute(renderer, "text", 1)
        self.own_ctrl.bind_property(
            "type_idx", self.types, "active", 
            GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )
        box_sel.append(self.types)
        self.types.connect("changed", self.on_type_changed)
        self.append(box_sel)
 
        ### Show/Hide Boxes and +
        self.bank_dual = Bank("DUAL DELAY", {'DELAY_1':'1', 'DELAY_2':'2'})
        self.bank_dual.buttons[0].set_active(True)
        self.bank_dual.hide()
        self.bank_dual.buttons[0].connect("toggled", self.on_delay_toggled)
        for but in self.bank_dual.buttons:
            but.get_style_context().add_class('smaller')
        self.append(self.bank_dual)

        ### Box Delay ###
        self.box_dly = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        self.box_dly.get_style_context().add_class('inner')
        label=Gtk.Label(label="Delay")
        label.set_xalign(1.0)
        label.set_margin_end(20)
        self.box_dly.append(label)

        self.time_lvl = Slider("Time", "long_time", self.own_ctrl, "time_lvl" )
        self.time_lvl.name = "time_lvl"
        #adj = self.time_lvl.scale.get_adjustment()
        #adj.set_lower(midi_str_to_int('00 01'))
        #adj.set_upper(midi_str_to_int('0f 50'))
        #self.time_lvl.set_format("t_time")
        #self.time_lvl.scale.set_format_value_func(self.format_t_time)
        # self.time_lvl.connect("value-changed", self.on_slider_changed)
        self.time_lvl.connect("delayed-value", self.on_slider_changed)
        self.time_lvl.show()
        self.box_dly.append(self.time_lvl)

        self.feedback_lvl = Slider("Feeback", "normal", self.own_ctrl, "feedback_lvl" )
        self.feedback_lvl.name = "feedback_lvl"
        #self.feedback_lvl.scale.set_format_value_func(self.format_time)
        # self.feedback_lvl.connect("value-changed", self.on_slider_changed)
        self.feedback_lvl.connect("delayed-value", self.on_slider_changed)
        self.feedback_lvl.show()
        self.box_dly.append(self.feedback_lvl)

            ## D1 Time ##
        self.d1_time_lvl = Slider("Time 1", "long_time", self.own_ctrl, "d1_time_lvl" )
        self.d1_time_lvl.name = "d1_time_lvl"
        #adj = self.d1_time_lvl.scale.get_adjustment()
        #adj.set_lower(midi_str_to_int('00 01'))
        #adj.set_upper(midi_str_to_int('0f 50'))
        #self.d1_time_lvl.set_format("t_time")
        #self.d1_time_lvl.scale.set_format_value_func(self.format_t_time)
        # self.d1_time_lvl.connect("value-changed", self.on_slider_changed)
        self.d1_time_lvl.connect("delayed-value", self.on_slider_changed)
        self.d1_time_lvl.hide()
        self.box_dly.append(self.d1_time_lvl)

        self.d1_fb_lvl = Slider("Feeback 1", "normal", self.own_ctrl, "d1_fb_lvl" )
        self.d1_fb_lvl.name = "d1_fb_lvl"
        #self.fb_lvl.scale.set_format_value_func(self.format_time)
        # self.d1_fb_lvl.connect("value-changed", self.on_slider_changed)
        self.d1_fb_lvl.connect("delayed-value", self.on_slider_changed)
        self.d1_fb_lvl.hide()
        self.box_dly.append(self.d1_fb_lvl)

            ## D2 Time ##
        self.d2_time_lvl = Slider("Time 2", "long_time", self.own_ctrl, "d2_time_lvl" )
        self.d2_time_lvl.name = "d2_time_lvl"
        #adj = self.d2_time_lvl.scale.get_adjustment()
        #adj.set_lower(midi_str_to_int('00 01'))
        #adj.set_upper(midi_str_to_int('0f 50'))
        #self.d2_time_lvl.set_format("t_time")
        #self.d2_time_lvl.scale.set_format_value_func(self.format_t_time)
        # self.d2_time_lvl.connect("value-changed", self.on_slider_changed)
        self.d1_time_lvl.connect("delayed-value", self.on_slider_changed)
        self.d2_time_lvl.hide()
        self.box_dly.append(self.d2_time_lvl)

        self.d2_fb_lvl = Slider("Feeback 2", "normal", self.own_ctrl, "d2_fb_lvl" )
        self.d2_fb_lvl.name = "d2_fb_lvl"
        #self.fb_lvl.scale.set_format_value_func(self.format_time)
        # self.d2_fb_lvl.connect("value-changed", self.on_slider_changed)
        self.d1_fb_lvl.connect("delayed-value", self.on_slider_changed)
        self.d2_fb_lvl.hide()
        self.box_dly.append(self.d2_fb_lvl)


        self.tap_time_lvl = Slider("Tap Time", "percent", self.own_ctrl, "tap_time_lvl" )
        self.tap_time_lvl.name = "tap_time_lvl"
        #self.tap_time_lvl.set_format("percent")
        #self.tap_time_lvl.scale.set_format_value_func(self.format_percent)
        # self.tap_time_lvl.connect("value-changed", self.on_slider_changed)
        self.tap_time_lvl.connect("delayed-value", self.on_slider_changed)
        self.box_dly.append(self.tap_time_lvl)
        self.tap_time_lvl.hide()
        self.append(self.box_dly)

        ## Box Filter
        self.box_filt = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        self.box_filt.get_style_context().add_class('inner')
        label=Gtk.Label(label="Filter")
        label.set_xalign(1.0)
        label.set_margin_end(20)
        self.box_filt.append(label)

        self.high_cut_lvl = Slider( "High Cut", "high_freq", self.own_ctrl, "high_cut_lvl" )
        self.high_cut_lvl.name = "high_cut_lvl"
        #adj = self.high_cut_lvl.scale.get_adjustment()
        #adj.set_upper(from_str('0e')[0])
        #adj.set_page_increment(1)
        #self.high_cut_lvl.set_format("high_freq")
        #self.high_cut_lvl.scale.set_format_value_func(self.format_high_freq)
        # self.high_cut_lvl.connect("value-changed", self.on_slider_changed)
        self.high_cut_lvl.connect("delayed-value", self.on_slider_changed)
        self.high_cut_lvl.show()
        self.box_filt.append(self.high_cut_lvl)
            ## D1 High_cut
        self.d1_h_cut_lvl = Slider( "High Cut 1", "high_freq", self.own_ctrl, "d1_h_cut_lvl" )
        self.d1_h_cut_lvl.name = "d1_h_cut_lvl"
        #adj = self.d1_h_cut_lvl.scale.get_adjustment()
        #adj.set_upper(from_str('0e')[0])
        #adj.set_page_increment(1)
        #self.d1_h_cut_lvl.set_format("high_freq")
        #self.d1_h_cut_lvl.scale.set_format_value_func(self.format_high_freq)
        # self.d1_h_cut_lvl.connect("value-changed", self.on_slider_changed)
        self.d1_h_cut_lvl.connect("delayed-value", self.on_slider_changed)
        self.d1_h_cut_lvl.hide()
        self.box_filt.append(self.d1_h_cut_lvl)
            ## D2 High_cut
        self.d2_h_cut_lvl = Slider( "High Cut 2", "high_freq", self.own_ctrl, "d2_h_cut_lvl" )
        self.d2_h_cut_lvl.name = "d2_h_cut_lvl"
        #adj = self.d2_h_cut_lvl.scale.get_adjustment()
        #adj.set_upper(from_str('0e')[0])
        #adj.set_page_increment(1)
        #self.d2_h_cut_lvl.set_format("high_freq")
        #self.d2_h_cut_lvl.scale.set_format_value_func(self.format_high_freq)
        # self.d2_h_cut_lvl.connect("value-changed", self.on_slider_changed)
        self.d2_h_cut_lvl.connect("delayed-value", self.on_slider_changed)
        self.d2_h_cut_lvl.hide()
        self.box_filt.append(self.d2_h_cut_lvl)

        self.append(self.box_filt)

        ## Box Level
        # self.box_lvl = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        # self.box_lvl.get_style_context().add_class('inner')
        # label=Gtk.Label(label="Level")
        # label.set_xalign(1.0)
        # label.set_margin_end(20)
        # self.box_lvl.append(label)

        ## Box SDE-3000
        self.box_sde = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        self.box_sde.hide()
        self.box_sde.get_style_context().add_class('inner')
        label=Gtk.Label(label="SDE-3000")
        label.set_xalign(1.0)
        label.set_margin_end(20)
        self.box_sde.append(label)

        box_h = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        self.sde_vint_lpf_sw = Toggle("Vintage LPF")
        self.sde_vint_lpf_sw.name = "sde_vint_lpf_sw"
        self.own_ctrl.bind_property(
            "sde_vint_lpf_sw", self.sde_vint_lpf_sw,
            "active", GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )
        #self.sde_vint_lpf_sw.connect("toggled", self.on_toggle_changed)
        box_h.append(self.sde_vint_lpf_sw)
        self.sde_fb_phase_sw = Toggle("Feedback Phase")
        self.sde_fb_phase_sw.name = "sde_fb_phase_sw"
        self.own_ctrl.bind_property(
            "sde_fb_phase_sw", self.sde_fb_phase_sw,
            "active", GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )
        #self.sde_fb_phase_sw.connect("toggled", self.on_toggle_changed)
        box_h.append(self.sde_fb_phase_sw)
        self.sde_ef_phase_sw = Toggle("Effect Phase")
        self.sde_ef_phase_sw.name = "sde_ef_phase_sw"
        self.own_ctrl.bind_property(
            "sde_ef_phase_sw", self.sde_fb_phase_sw,
            "active", GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )
        #self.sde_fb_phase_sw.connect("toggled", self.on_toggle_changed)
        box_h.append(self.sde_ef_phase_sw)
        self.box_sde.append(box_h)
        box_h2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        self.sde_filter_sw = Toggle("Filter")
        self.sde_filter_sw.name = "sde_filter_sw"
        self.own_ctrl.bind_property(
            "sde_filter_sw", self.sde_filter_sw,
            "active", GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )
        #self.sde_filter_sw.connect("toggled", self.on_toggle_changed)
        box_h2.append(self.sde_filter_sw)
        self.sde_modul_sw = Toggle("Modulation")
        self.sde_modul_sw.name = "sde_modul_sw"
        self.own_ctrl.bind_property(
            "sde_modul_sw", self.sde_modul_sw,
            "active", GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )
        #self.sde_modul_sw.connect("toggled", self.on_toggle_changed)
        box_h2.append(self.sde_modul_sw)
        self.box_sde.append(box_h2)
        self.append(self.box_sde)

        ## Box Modulation
        self.box_mod = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        self.box_mod.hide()
        self.box_mod.get_style_context().add_class('inner')
        label=Gtk.Label(label="Modulate")
        label.set_xalign(1.0)
        label.set_margin_end(20)
        self.box_mod.append(label)

        self.mod_rate_lvl = Slider("Rate", "normal", self.own_ctrl, "mod_rate_lvl" )
        self.mod_rate_lvl.name = "mod_rate_lvl"
        # self.mod_rate_lvl.connect("value-changed", self.on_slider_changed)
        self.mod_rate_lvl.connect("delayed-value", self.on_slider_changed)
        self.box_mod.append(self.mod_rate_lvl)

        self.mod_depth_lvl = Slider("Depth", "normal", self.own_ctrl, "mod_depth_lvl" )
        self.mod_depth_lvl.name = "mod_depth_lvl"
        # self.mod_depth_lvl.connect("value-changed", self.on_slider_changed)
        self.mod_depth_lvl.connect("delayed-value", self.on_slider_changed)
        self.box_mod.append(self.mod_depth_lvl)
        
        self.append(self.box_mod)

        #Levels
        self.effect_lvl = Slider( "Effect", "normal", self.own_ctrl, "effect_lvl" )
        self.effect_lvl.get_style_context().add_class('inner')
        self.effect_lvl.name = "effect_lvl"
        # self.effect_lvl.connect("value-changed", self.on_slider_changed)
        self.effect_lvl.connect("delayed-value", self.on_slider_changed)
        self.effect_lvl.show()
        self.append(self.effect_lvl)

        self.d1_eff_lvl = Slider( "Effect 1", "normal", self.own_ctrl, "d1_eff_lvl" )
        self.d1_eff_lvl.get_style_context().add_class('inner')
        self.d1_eff_lvl.name = "d1_eff_lvl"
        # self.d1_eff_lvl.connect("value-changed", self.on_slider_changed)
        self.d1_eff_lvl.connect("delayed-value", self.on_slider_changed)
        self.d1_eff_lvl.hide()
        self.append(self.d1_eff_lvl)

        self.d2_eff_lvl = Slider( "Effect 2", "normal", self.own_ctrl, "d2_eff_lvl" )
        self.d2_eff_lvl.get_style_context().add_class('inner')
        self.d2_eff_lvl.name = "d2_eff_lvl"
        # self.d2_eff_lvl.connect("value-changed", self.on_slider_changed)
        self.d2_eff_lvl.connect("delayed-value", self.on_slider_changed)
        self.d2_eff_lvl.hide()
        self.append(self.d2_eff_lvl)

        self.dirmix_lvl = Slider( "Direct Mix", "normal", self.own_ctrl, "dirmix_lvl" )
        self.dirmix_lvl.get_style_context().add_class('outer')
        self.dirmix_lvl.name = "dirmix_lvl"
        # self.dirmix_lvl.connect("value-changed", self.on_slider_changed)
        self.dirmix_lvl.connect("delayed-value", self.on_slider_changed)
        #self.box_lvl.append(self.dirmix_lvl)

        self.append(self.dirmix_lvl)

        self.own_ctrl.connect("delay-map-ready", self.on_delay_loaded)

    def on_delay_toggled(self, button):
        #st = button.get_active()
        self.on_type_changed(self.types)

    def on_type_changed(self, types):
        idx = types.get_active()
        #log.debug(f"{idx=}")
        base_widgets = [
            self.box_dly,       # 0
            self.time_lvl,      # 1
            self.feedback_lvl,  # 2
            self.effect_lvl,    # 3
            self.high_cut_lvl,  # 4
            self.box_filt,      # 5
            self.tap_time_lvl,  # 6
            self.box_mod,       # 7
            self.box_sde,       # 8
            self.bank_dual,     # 9
        ]
        duals = [
            self.d1_time_lvl,
            self.d1_fb_lvl,
            self.d1_h_cut_lvl,
            self.d1_eff_lvl,
            self.d2_time_lvl,
            self.d2_fb_lvl,
            self.d2_h_cut_lvl,
            self.d2_eff_lvl, 
        ]
        for w in base_widgets + duals:
            w.hide()

        if idx in [0, 1, 6, 7, 8, 9]:
            for i in [0, 1, 2, 3, 4, 5]:
                base_widgets[i].show()
            if idx == 1:
                base_widgets[6].show()
            elif idx == 9:
                base_widgets[7].show()
        elif idx in [2, 3, 4, 5]:
            for i in [0,5,9]:
                base_widgets[i].show()
            dn = self.bank_dual.selected
            #log.debug(f"{dn=}")
            for i in range(4):
                name = duals[i + dn*4].name
                # log.debug(name)
                duals[i + dn*4].show()
        elif idx == 10:
            for i in [0,1,2,3,8]:
                base_widgets[i].show()

    def on_slider_changed( self, slider, value):
        self.own_ctrl.set_property(slider.name, int(value))

    def on_delay_loaded(self, device, types):
        i = 0
        for name, code in types.items():
            self.types_store.append([i,name, code])
            i += 1
        i = 0


