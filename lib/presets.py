
from gi.repository import GObject

class Preset(GObject.GObject):
    name = GObject.Property(type=str)
    label = GObject.Property(type=str)
    num = GObject.Property(type=int)

