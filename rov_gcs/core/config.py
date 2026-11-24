import json
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "settings.json"


def load_config(path=CONFIG_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)