import json
import logging
from pathlib import Path

log = logging.getLogger(__name__)

PROFILE_DIR = Path(__file__).resolve().parents[2] / "config" / "profiles"


def list_profiles(directory=PROFILE_DIR):
    return sorted(p.stem for p in Path(directory).glob("*.json"))


def load_profile(name, directory=PROFILE_DIR):
    with open(Path(directory) / f"{name}.json", "r", encoding="utf-8") as f:
        return json.load(f)


def save_profile(name, data, directory=PROFILE_DIR):
    Path(directory).mkdir(parents=True, exist_ok=True)
    with open(Path(directory) / f"{name}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def find_profile_for_controller(controller_name, directory=PROFILE_DIR):
    for name in list_profiles(directory):
        hint = load_profile(name, directory).get("controller", "")
        if hint and hint.lower() in controller_name.lower():
            return name
    return "default"


class ProfileManager:
    """Loads profiles on request or when a known controller connects."""

    def __init__(self, bus, directory=PROFILE_DIR):
        self.bus = bus
        self.directory = directory
        self.active = None
        bus.subscribe("input.device", self._on_device)
        bus.subscribe("profile.load", self.apply)

    def apply(self, name):
        try:
            data = load_profile(name, self.directory)
        except (OSError, ValueError):
            log.exception("Could not load profile %s", name)
            return
        self.active = name
        log.info("Profile applied: %s", name)
        self.bus.publish("profile.applied", {"name": name, "data": data})

    def _on_device(self, event):
        if event.get("event") == "connected":
            name = find_profile_for_controller(event.get("name", ""), self.directory)
            self.apply(name)