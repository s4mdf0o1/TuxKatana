import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib#, Gdk

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from math import isfinite
import numpy as np
import sounddevice as sd
import time
import threading

FS = 44100
WINDOW_SIZE = 8192
BLOCKSIZE = 1024
HOP_TIME = 0.04
RMS_THRESHOLD = 1e-4
SMOOTH_ALPHA = 0.6 
BAR_SPAN = 10.0
BAR_WIDTH = 24
YIN_THRESHOLD = 0.1
TARGET_FREQS = { 
    'E₂': 82.41, 'A₂': 110.00, 'D₃': 146.83,
    'G₃': 196.00, 'B₃': 246.94, 'E₄': 329.63
}

class Tuner:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.buffer = np.zeros(WINDOW_SIZE, dtype='float32')
        self.buf_lock = threading.Lock()
        self.stop_flag = False
        self.detected_freq = 0.0
        self.prev_freq = 0.0

    def get_closest_string(self, freq):
        return min(TARGET_FREQS.items(), key=lambda x: abs(x[1] - freq))

    def lerp(self, a, b, t): return int(round(a + (b - a) * t))

    def rgb_for_diff(self, diff_hz, span):
        t = max(-1.0, min(1.0, diff_hz / span))
        if t <= -0.5:
            s = (t + 1.0) / 0.5
            r, g, b = 0, self.lerp(0, 255, s), 255
        elif t <= 0.0:
            s = (t + 0.5) / 0.5
            r, g, b = 0, 255, self.lerp(255, 0, s)
        elif t <= 0.5:
            s = (t - 0.0) / 0.5
            r, g, b = self.lerp(0, 255, s), 255, 0
        else:
            s = (t - 0.5) / 0.5
            r, g, b = 255, self.lerp(255, 0, s), 0
        return r, g, b

    def ansi_truecolor(self, r,g,b): return f"<span foreground='#{r:02x}{g:02x}{b:02x}'>"

    def freq_to_bar_pango(self, current, target, width=BAR_WIDTH, span=BAR_SPAN):
        low, high = target - span/2, target + span/2
        rng, center = high - low, width//2
        chars = []
        for i in range(width):
            pos_freq = low + (i/(width-1))*rng
            diff_pos = pos_freq - target
            r,g,b = self.rgb_for_diff(diff_pos, span/2)
            col = self.ansi_truecolor(r,g,b)
            ch = '◎' if i==center else '▢' #'-'
            chars.append(f"{col}{ch}</span>")
        cur_pos = int(round((current - low) / rng * (width - 1)))
        cur_pos = max(0, min(width - 1, cur_pos))
        cur_diff = current - target
        r,g,b = self.rgb_for_diff(cur_diff, span/2)
        cursor_col = self.ansi_truecolor(r,g,b)
        cursor_sym = '◉' if cur_pos==center else '▶' if cur_pos < center else '◀' # '⭠'
        chars[cur_pos] = f"{cursor_col}{cursor_sym}</span>"
        return ''.join(chars)

    def yin_pitch(self, signal, fs, fmin=60, fmax=1000, threshold=YIN_THRESHOLD):
        N = len(signal)
        max_tau = int(fs / fmin)
        min_tau = int(fs / fmax)
        diff = np.zeros(max_tau)
        for tau in range(1, max_tau):
            diff[tau] = np.sum((signal[:N - tau] - signal[tau:N])**2)
        cum_sum = np.cumsum(diff[1:])
        cmndf = np.ones(max_tau)
        cmndf[1:] = diff[1:] * np.arange(1, max_tau) / (cum_sum + 1e-8)
        tau = min_tau
        while tau < max_tau:
            if cmndf[tau] < threshold:
                while tau+1 < max_tau and cmndf[tau+1] < cmndf[tau]:
                    tau += 1
                break
            tau += 1
        else:
            return 0.0
        if 1 < tau < max_tau-1:
            s0,s1,s2 = cmndf[tau-1],cmndf[tau],cmndf[tau+1]
            denom = (s0+s2-2*s1)
            if denom != 0:
                tau += 0.5*(s0-s2)/denom
        return fs/tau

    def audio_callback(self, indata, frames, time_info, status):
        # global buffer
        mono = indata[:,0].astype('float32')
        with self.buf_lock:
            f = len(mono)
            if f >= WINDOW_SIZE: self.buffer[:] = mono[-WINDOW_SIZE:]
            else:
                self.buffer[:-f] = self.buffer[f:]
                self.buffer[-f:] = mono

    def processing_thread(self, dialog=None):
        # global detected_freq, prev_freq, stop_flag
        while not self.stop_flag:
            time.sleep(HOP_TIME)
            with self.buf_lock: x = self.buffer.copy()
            if np.max(np.abs(x)) < 1e-8: continue
            x -= np.mean(x); rms = np.sqrt(np.mean(x*x))
            if rms < RMS_THRESHOLD:
                # if dialog:
                GLib.idle_add(self.update_display, "--", 0.0, 0.0, " " * BAR_WIDTH)

                continue
            xw = x * np.hanning(len(x))
            freq = self.yin_pitch(xw, FS)
            if freq <= 0 or not isfinite(freq):
                # if dialog:
                GLib.idle_add(self.update_display, "--", 0.0, 0.0, " " * BAR_WIDTH)

                continue
            out = freq if self.prev_freq==0.0 else SMOOTH_ALPHA*freq+(1.0-SMOOTH_ALPHA)*self.prev_freq
            self.prev_freq = out; self.detected_freq = out
            # if dialog:
            note,target = self.get_closest_string(out)
            offset = out - target
            bar = self.freq_to_bar_pango(out, target)
            GLib.idle_add(self.update_display, note, out, offset, bar)

class TunerDialog(Tuner, Gtk.Dialog):
    def __init__(self, app, parent):
        super().__init__(title="Tuner", transient_for=parent, modal=True)
        self.set_default_size(400,100)
        self.set_decorated(False)
        # self.add_buttons("_Close", Gtk.ResponseType.CLOSE)


        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_halign(Gtk.Align.CENTER)
        vbox.set_valign(Gtk.Align.CENTER)
        self.set_child(vbox)

        self.note_label = Gtk.Label()
        self.note_label.set_markup("<span font='24'>E-A-D-G-B-E</span>")
        self.note_label.set_xalign(0.5)
        vbox.append(self.note_label)

        self.bar_label = Gtk.Label()
        self.bar_label.set_use_markup(True)
        self.bar_label.set_xalign(0.5)
        self.bar_label.set_selectable(True)
        self.bar_label.set_margin_bottom(40)
        vbox.append(self.bar_label)

        btn_close = Gtk.Button(label="Close")
        btn_close.set_hexpand(False)
        btn_close.connect("clicked", lambda b: self.close())
        vbox.append(btn_close)

    def update_display(self, note, freq, offset, bar_markup):
        r,g,b = self.rgb_for_diff(offset, BAR_SPAN/2)
        color = f"#{r:02x}{g:02x}{b:02x}"
        self.note_label.set_markup(f"<span foreground='{color}' font='24'>{note}</span>")
        self.bar_label.set_markup(bar_markup)

    def find_katana_device(self):
        # devices = sd.query_devices()
        # for idx, dev in enumerate(devices):
        #     if "katana_mirror.monitor" in dev['name'].lower() and dev['max_input_channels']>0:
        #         return idx
        # raise RuntimeError("Katana monitor not found")
        # devices = sd.query_devices()
        # for idx, dev in enumerate(devices):
        #     name = dev['name'].lower()
        #     if "katana" in name and "line4" in name and dev['max_input_channels'] > 0:
        #         return idx
        # raise RuntimeError("Katana DI Capture not found")

        devices = sd.query_devices()
        for idx, dev in enumerate(devices):
            if "pulse" in dev['name'] and dev['max_input_channels']>0:
                # log.debug(idx)
                time.sleep(0.05)
                return idx
        raise RuntimeError("Katana sound device not found")


