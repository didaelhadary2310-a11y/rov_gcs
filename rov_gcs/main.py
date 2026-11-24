import logging
import time

from rov_gcs.core.config import load_config
from rov_gcs.core.event_bus import EventBus
from rov_gcs.core.log_setup import setup_logging
from rov_gcs.input.input_thread import InputThread
from rov_gcs.input.profiles import ProfileManager, list_profiles

log = logging.getLogger("rov_gcs")


def main():
    cfg = load_config()
    setup_logging(cfg["logging"]["level"], cfg["logging"]["file"])
    bus = EventBus()

    def on_key(event):
        log.info("key %s", event)
        if event["down"] and event["key"].isdigit():
            names = list_profiles()
            index = int(event["key"]) - 1
            if 0 <= index < len(names):
                bus.publish("profile.load", names[index])

    bus.subscribe("input.key", on_key)
    bus.subscribe("input.device", lambda e: log.warning("device %s", e))
    bus.subscribe("profile.applied", lambda e: log.info("profile %s", e["name"]))
    profiles = ProfileManager(bus)
    thread = InputThread(
        bus, cfg["input"]["sample_rate_hz"], cfg["input"]["dead_zone"]
    )
    thread.start()
    try:
        while thread.is_alive():
            time.sleep(0.2)
    except KeyboardInterrupt:
        thread.stop()
        thread.join()


if __name__ == "__main__":
    main()