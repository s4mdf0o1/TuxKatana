import os
import json

from gi.repository import GLib, GObject, Gio

from ruamel.yaml import YAML
yaml = YAML(typ="rt")

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from .tools import *

class TSLFile:#(GObject.GObject):
    # __gsignals__ = {
    #     "modfx-map-ready": (GObject.SIGNAL_RUN_FIRST, None, (object,object,)),
    # }
    def __init__(self, device):
        super().__init__()
        self.device = device
        with open("params/format_preset.yaml", 'r') as f:
            self.map = yaml.load(f)
        self.data={}
        self.preset_name = "TODO"
        self.revision = "0002"      # to understand
        self.device_name = "KATANA Mk2"  # to get from device name
        self.memo = ""              # can be used
        self.dir_path = os.getcwd() + "/presets"

    def load(self, filename):
        self.filename = filename
        with open(filename, 'r') as f:
            self.data = json.load(f)

    def generate(self):
        tsl = {}
        tsl['name'] = self.preset_name
        tsl['formatRev'] = self.revision
        tsl['device'] = self.device_name.replace('2', 'II')
        tsl['data'] = [[]]
        tsl['data'][0].append({})
        infos = tsl['data'][0][0]
        infos['memo'] = { 'memo': self.memo, "isToneCentralPatch": True}
        infos['paramSet'] = {}
        ps = infos['paramSet']
        offset = 0
        old_Addr = self.device.mry.Addr_start
        old_size = 0
        for k, vals in self.map.items():
            #log.debug(f"{to_str(self.device.mry.offset_to_addr(offset))=}")
            Addr = self.device.mry.Addr_start
            offset += vals['offset']
            Addr += offset
            old_Addr = Addr - old_size
            #log.debug(f"{old_Addr} = {Addr} - {old_size}")
            old_size = vals['size']
            #log.debug(f"{Addr} / size:{vals['size']} ofs:{vals['offset']}")
            data = self.device.mry.read(Addr, vals['size'], True).upper().split(' ')
            log.debug(f"{k}:> '{Addr}': {len(data)} {vals['offset']}")
            if len(data) < vals['size']:
                log.debug(data)
            ps[k] = self.device.mry.read(Addr, vals['size'], True).upper().split(' ')
            offset += vals['size']
        # log.debug(tsl)
        return tsl

    def save(self, filename="test.tsl"):
        self.filename = filename
        file_path = self.dir_path + '/' + filename
        with open(file_path, 'w') as f:
            json.dump(self.generate(), f)
        log.info(f"Preset saved to: {file_path}")


