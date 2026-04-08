import json
from .exceptions import ConfigError

REQUIRED_KEYS = [
    ("business", "name"),
    ("business", "website"),
    ("business", "email"),
    ("smtp", "host"),
    ("smtp", "username"),
    ("smtp", "password"),
    ("rate_limit", "min_delay_s"),
    ("rate_limit", "max_delay_s"),
]

def load_config(path: str = "config.json") -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        raise ConfigError(f"Config file not found: {path}")
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in config file: {e}")

    for keys in REQUIRED_KEYS:
        node = config
        for key in keys:
            if not isinstance(node, dict) or key not in node:
                raise ConfigError(f"Missing required config key: {'.'.join(keys)}")
            node = node[key]

    return config
