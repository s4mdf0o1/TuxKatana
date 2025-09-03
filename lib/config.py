from ruamel.yaml import YAML
yaml = YAML(typ="safe")
from collections import UserDict

class Config(UserDict):
    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath
        with open(filepath, 'r') as f:
            self.data = yaml.load(f) or {}

    def save(self):
        """Réécrit le YAML à partir du dict actuel."""
        with open(self.filepath, 'w') as f:
            yaml.dump(self.data, f)

    def get_int(self, key, default=0):
        """Récupère une valeur et la convertit en int."""
        return int(self.data.get(key, default))

    def __repr__(self):
        return f"<Config {self.filepath} keys={list(self.data.keys())}>"


