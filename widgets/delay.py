import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk, GObject

from .slider import Slider
from .tabbed_panel import TabbedPanel
from .bank import Bank
from .toggle import Toggle
from .combo_store import ComboStore
from .box_inner import BoxInner
from lib.effect import Effect

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from lib.set_mapping import add_properties
@add_properties()
class Delay(Effect, Gtk.Box):
    delay_sw        = GObject.Property(type=bool, default=False)
    de_type         = GObject.Property(type=str)
    de_type_idx     = GObject.Property(type=int, default=0)
    de_status       = GObject.Property(type=int, default=0)
    de_bank_sel     = GObject.Property(type=int, default=0)
    de_type_G       = GObject.Property(type=int, default=0)
    de_type_R       = GObject.Property(type=int, default=0)
    de_type_Y       = GObject.Property(type=int, default=0)
    de_time_lvl     = GObject.Property(type=float, default=0.0)
    de_feedback_lvl = GObject.Property(type=int, default=0)
    de_tap_time_lvl = GObject.Property(type=int, default=0)
    de_high_cut_lvl = GObject.Property(type=int, default=0)
    de_effect_lvl   = GObject.Property(type=int, default=0)
    de_dmix_lvl     = GObject.Property(type=int, default=0)
    de_x_time_lvl     = GObject.Property(type=float, default=0.0)
    de_x_fb_lvl       = GObject.Property(type=int, default=0)
    de_x_h_cut_lvl    = GObject.Property(type=int, default=0)
    de_x_eff_lvl      = GObject.Property(type=int, default=0)
    de_y_time_lvl     = GObject.Property(type=float, default=0.0)
    de_y_fb_lvl       = GObject.Property(type=int, default=0)
    de_y_h_cut_lvl    = GObject.Property(type=int, default=0)
    de_y_eff_lvl      = GObject.Property(type=int, default=0)
    de_mod_rate_lvl    = GObject.Property(type=int, default=0)
    de_mod_depth_lvl   = GObject.Property(type=int, default=0)
    de_sde_vint_lpf_sw = GObject.Property(type=bool, default=False)
    de_sde_fb_phase_sw = GObject.Property(type=bool, default=False)
    de_sde_ef_phase_sw = GObject.Property(type=bool, default=False)
    de_sde_filter_sw   = GObject.Property(type=bool, default=False)
    de_sde_modul_sw    = GObject.Property(type=bool, default=False)
    de_vol_lvl   = GObject.Property(type=int, default=0)


    def __init__(self, ctrl):
        super().__init__(ctrl, self.mapping)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(6)
        
        banks = {"GREEN":'1', "RED":'2', "YELLOW":'3'}
        self.bank_select = Bank("DELAY", banks)
        self.bank_select.buttons[0].set_status_id(1)
        self.bank_select.buttons[2].set_status_id(3)
        self.append(self.bank_select)

        self.bind_property(
            "de_bank_sel", self.bank_select, "selected",
            GObject.BindingFlags.BIDIRECTIONAL |\
            GObject.BindingFlags.SYNC_CREATE )

        box_sel = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        self.types_store = ComboStore( self, self.types, 'de_type_idx')
        box_sel.append(self.types_store)
        self.types_store.connect("changed", self.on_type_changed)
        self.volume = Slider( 
                "Volume", "normal", self, "de_vol_lvl" )
        box_sel.append(self.volume)
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
        self.box_dly = BoxInner("Delay")
        self.time = Slider(
                "Time", "long_time", self, "de_time_lvl" )
        self.time.show()
        self.box_dly.append(self.time)

        self.feedback = Slider("Feeback", "normal", self, "de_feedback_lvl" )
        self.feedback.show()
        self.box_dly.append(self.feedback)

            ## D1 Time ##
        self.de_x_time= Slider(
                "Time 1", "long_time", self, "de_x_time_lvl" )
        self.de_x_time.hide()
        self.box_dly.append(self.de_x_time)

        self.de_x_fb= Slider(
                "Feeback 1", "normal", self, "de_x_fb_lvl" )
        self.de_x_fb.hide()
        self.box_dly.append(self.de_x_fb)

            ## D2 Time ##
        self.de_y_time= Slider(
                "Time 2", "long_time", self, "de_y_time_lvl" )
        self.de_y_time.hide()
        self.box_dly.append(self.de_y_time)

        self.de_y_fb= Slider(
                "Feeback 2", "normal", self, "de_y_fb_lvl" )
        self.de_y_fb.hide()
        self.box_dly.append(self.de_y_fb)


        self.tap_time= Slider(
                "Tap Time", "percent", self, "de_tap_time_lvl" )
        self.tap_time.hide()
        self.box_dly.append(self.tap_time)
        self.append(self.box_dly)

        ## Box Filter
        self.box_filt = BoxInner("Filter")
        self.high_cut= Slider(
                "High Cut", "high_freq", self, "de_high_cut_lvl" )
        self.high_cut.show()
        self.box_filt.append(self.high_cut)
            ## D1 High_cut
        self.de_x_h_cut= Slider(
                "High Cut 1", "high_freq", self, "de_x_h_cut_lvl" )
        self.de_x_h_cut.hide()
        self.box_filt.append(self.de_x_h_cut)
            ## D2 High_cut
        self.de_y_h_cut= Slider(
                "High Cut 2", "high_freq", self, "de_y_h_cut_lvl" )
        self.de_y_h_cut.hide()
        self.box_filt.append(self.de_y_h_cut)

        self.append(self.box_filt)

        ## Box SDE-3000
        self.box_sde = BoxInner("SDE-3000")
        self.box_sde.hide()
        box_h = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        self.de_sde_vint_lpf = Toggle("Vintage LPF")
        self.bind_property(
            "de_sde_vint_lpf_sw", self.de_sde_vint_lpf,
            "active", GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )
        box_h.append(self.de_sde_vint_lpf)
        self.de_sde_fb_phase = Toggle("Feedback Phase")
        self.bind_property(
            "de_sde_fb_phase_sw", self.de_sde_fb_phase,
            "active", GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )
        box_h.append(self.de_sde_fb_phase)
        self.de_sde_ef_phase = Toggle("Effect Phase")
        self.bind_property(
            "de_sde_ef_phase_sw", self.de_sde_ef_phase,
            "active", GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )
        box_h.append(self.de_sde_ef_phase)
        self.box_sde.append(box_h)
        box_h2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        self.de_sde_filter= Toggle("Filter")
        self.bind_property(
            "de_sde_filter_sw", self.de_sde_filter,
            "active", GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )
        box_h2.append(self.de_sde_filter)
        self.de_sde_modul= Toggle("Modulation")
        self.bind_property(
            "de_sde_modul_sw", self.de_sde_modul,
            "active", GObject.BindingFlags.SYNC_CREATE |\
            GObject.BindingFlags.BIDIRECTIONAL )
        box_h2.append(self.de_sde_modul)
        self.box_sde.append(box_h2)
        self.append(self.box_sde)

        ## Box Modulation
        self.box_mod = BoxInner("Modulate")
        self.box_mod.hide()
        self.mod_rate= Slider(
                "Rate", "normal", self, "de_mod_rate_lvl" )
        self.box_mod.append(self.mod_rate)

        self.mod_depth= Slider(
                "Depth", "normal", self, "de_mod_depth_lvl" )
        self.box_mod.append(self.mod_depth)
        
        self.append(self.box_mod)

        #Levels
        self.effect= Slider(
                "Effect", "normal", self, "de_effect_lvl" )
        self.effect.get_style_context().add_class('inner')
        self.effect.show()
        self.append(self.effect)

        self.de_x_eff= Slider(
                "Effect 1", "normal", self, "de_x_eff_lvl" )
        self.de_x_eff.get_style_context().add_class('inner')
        self.de_x_eff.hide()
        self.append(self.de_x_eff)

        self.de_y_eff= Slider(
                "Effect 2", "normal", self, "de_y_eff_lvl" )
        self.de_y_eff.get_style_context().add_class('inner')
        self.de_y_eff.hide()
        self.append(self.de_y_eff)

        self.dirmix= Slider(
                "Direct Mix", "normal", self, "de_dmix_lvl" )
        self.dirmix.get_style_context().add_class('outer')

        self.append(self.dirmix)

    def on_delay_toggled(self, button):
        self.on_type_changed(self.types)

    def on_type_changed(self, types):
        idx = types.get_active()
        base_widgets = [
            self.box_dly,       # 0
            self.time,      # 1
            self.feedback,  # 2
            self.effect,    # 3
            self.high_cut,  # 4
            self.box_filt,      # 5
            self.tap_time,  # 6
            self.box_mod,       # 7
            self.box_sde,       # 8
            self.bank_dual,     # 9
        ]
        duals = [
            self.de_x_time,
            self.de_x_fb,
            self.de_x_h_cut,
            self.de_x_eff,
            self.de_y_time,
            self.de_y_fb,
            self.de_y_h_cut,
            self.de_y_eff, 
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
            for i in range(4):
                name = duals[i + dn*4].name
                duals[i + dn*4].show()
        elif idx == 10:
            for i in [0,1,2,3,8]:
                base_widgets[i].show()

    def on_slider_changed( self, slider, value):
        old_val = self.get_property(slider.name)
        value = int(value)
        # log.debug(f"{old_val} {value}")
        if value != old_val:
            self.set_property(slider.name, value)

    def on_delay_loaded(self, device, types):
        i = 0
        for name, code in types.items():
            self.types_store.append([i,name, code])
            i += 1
        i = 0


