import logging
import time

from rov_gcs.core.config import load_config
from rov_gcs.core.event_bus import EventBus
from rov_gcs.core.log_setup import setup_logging
from rov_gcs.input.input_thread import InputThread

log = logging.getLogger("rov_gcs")


def main():
    cfg = load_config()
    setup_logging(cfg["logging"]["level"], cfg["logging"]["file"])
    bus = EventBus()
    bus.subscribe("input.key", lambda e: log.info("key %s", e))
    bus.subscribe("input.device", lambda e: log.warning("device %s", e))
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