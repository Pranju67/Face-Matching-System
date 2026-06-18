"""
FaceMatch Pro - Settings Manager
Persists user preferences to data/settings.json
"""

import json
import os
from typing import Any

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "data", "settings.json")

DEFAULTS = {
    "theme": "dark",
    "similarity_threshold": 60.0,
    "mongo_host": "localhost",
    "mongo_port": 27017,
    "export_path": os.path.join(os.path.dirname(__file__), "reports"),
    "window_width": 1400,
    "window_height": 860,
    "auto_save_pdf": False,
}


class Settings:
    def __init__(self):
        self._data = dict(DEFAULTS)
        self._load()

    def _load(self):
        try:
            if os.path.exists(SETTINGS_PATH):
                with open(SETTINGS_PATH, "r") as f:
                    stored = json.load(f)
                    self._data.update(stored)
        except Exception:
            pass

    def save(self):
        os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
        try:
            with open(SETTINGS_PATH, "w") as f:
                json.dump(self._data, f, indent=2)
        except Exception:
            pass

    def get(self, key: str, fallback: Any = None) -> Any:
        return self._data.get(key, fallback if fallback is not None else DEFAULTS.get(key))

    def set(self, key: str, value: Any):
        self._data[key] = value
        self.save()

    def update(self, d: dict):
        self._data.update(d)
        self.save()

    def reset(self):
        self._data = dict(DEFAULTS)
        self.save()


_instance = None

def get_settings() -> Settings:
    global _instance
    if _instance is None:
        _instance = Settings()
    return _instance
