import os
import json

from gi.repository import GLib, GObject, Gio

from ruamel.yaml import YAML
yaml = YAML(typ="rt")

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from .tools import *

class TSLFile(GObject.GObject):
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

    def load(self, filename):
        self.filename = filename
        with open(filename, 'r') as f:
            self.data = json.load(f)

    def generate(self):
        tsl = {}
        tsl['name'] = self.preset_name
        tsl['formatRev'] = self.revision
        tsl['device'] = self.device_name
        tsl['data'] = [[]]
        tsl['data'][0].append({})
        infos = tsl['data'][0][0]
        infos['memo'] = { 'memo': self.memo, "isToneCentralPatch": True}
        infos['paramSet'] = {}
        ps = infos['paramSet']
        offset = 0
        for k, size in self.map.items():
            if k == 'UserPatch%PatchName':
                ps[k] = self.device.preset_name
            else:
                log.debug(f"{to_str(self.device.mry.offset_to_addr(offset))=}")
                saddr = to_str(self.device.mry.offset_to_addr(offset))
                ps[k] = self.device.mry.get_block(saddr, size)
            offset += size
        log.debug(tsl)
        return tsl



    def save(self, filename="test.tsl"):
        self.filename = filename
        with open(filename, 'w') as f:
            json.dump(self.generate(), f)


