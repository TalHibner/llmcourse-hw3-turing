"""Configuration loading and management."""

import yaml
from pathlib import Path
from typing import Dict, Any


def load_config(config_file: str = "config/config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_file: Path to configuration file

    Returns:
        Configuration dictionary
    """
    config_path = Path(config_file)

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    return config


def get_config_value(config: Dict[str, Any], *keys, default=None):
    """
    Get nested configuration value.

    Args:
        config: Configuration dictionary
        *keys: Sequence of keys to traverse
        default: Default value if key not found

    Returns:
        Configuration value or default
    """
    value = config
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    return value
