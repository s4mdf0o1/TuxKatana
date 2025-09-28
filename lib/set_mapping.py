from ruamel.yaml import YAML
yaml = YAML(typ="rt")
import os
from gi.repository import GObject

import logging
from lib.log_setup import LOGGER_NAME
log = logging.getLogger(LOGGER_NAME)

from bidict import bidict
from .midi_bytes import Address, MIDIBytes

import re

def camel_to_snake(name: str) -> str:
    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def get_prefix(lower):
    return lower[:2]+'_' if len(lower.split())==1 \
            else ''.join(v[:1] for v in lower.split())+'_'

def add_properties():#, name, mapping):
    def decorator(cls):
        setattr(cls, 'name', cls.__name__)
        lower = cls.__name__.lower()
        setattr(cls, 'prefix', get_prefix(lower))
        snake = camel_to_snake(cls.__name__)
        # print(f"{lower=} {snake=}")

        filename = f"params/{snake}.yaml"
        if not os.path.exists(filename):
            filename = f"params/modfx/{snake}.yaml"
            if not os.path.exists(filename):
                raise FileNotFoundError(f"YAML not found: {filename}")
        with open(filename, "r", encoding="utf-8") as f:
            data = yaml.load(f)

        mry_map = {}
        for prop, addr in data.get("SEND", {}).items():
            mry_map[prop] = Address(addr)
        for addr, prop in data.get("RECV", {}).items():
            mry_map[prop] = Address(addr)
        setattr(cls, 'mapping', bidict(mry_map))

        for key in ['Types', 'Modes']:
            tmap = data.get(key, {})
            # log.debug(tmap)
            if tmap:
                # for name, val in tmap.items():
                    # tmap[name] = MIDIBytes(val).int
                setattr(cls, key.lower(), bidict(tmap))

        return cls
    return decorator

