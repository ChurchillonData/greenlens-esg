"""Load project settings from config.yaml and .env."""

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()


def load_config() -> dict:
    """Read config.yaml from the project root."""
    config_path = Path(__file__).resolve().parents[2] / "config.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


def get_api_key(name: str) -> str:
    """Read an API key from the environment, raise if missing."""
    key = os.getenv(name)
    if not key:
        raise RuntimeError(f"Missing environment variable: {name}. Check your .env file.")
    return key


CONFIG = load_config()