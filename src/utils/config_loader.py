from pathlib import Path
from pprint import pprint
from typing import Any

import yaml

def load_yaml_config(config_path:Path) -> Any:
    """Load a YAML configuration file and return its contents as a Python object."""
    with open(config_path, 'r', encoding='utf-8') as file:
        safe_load = yaml.safe_load(file)
    return safe_load