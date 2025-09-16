from gi.repository import GObject

from .tsl import TSLFile

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

class Presets(GObject.GObject):
    name = GObject.Property(type=str)
    label = GObject.Property(type=str)
    num = GObject.Property(type=int)

class Preset(TSLFile, GObject.GObject):
    def __init__(self, device):
        super().__init__(device)
        #self.tsl = TSLFile(device)

    def gen(self):
        self.save()
