import logging
import threading
import time

import pygame

from rov_gcs.input.deadzone import apply_deadzone

log = logging.getLogger(__name__)


class InputThread(threading.Thread):
    """Samples keyboard and game controller at a fixed rate."""

    def __init__(self, bus, rate_hz=50, dead_zone=0.1):
        super().__init__(name="InputThread", daemon=True)
        self.bus = bus
        self.period = 1.0 / rate_hz
        self.dead_zone = dead_zone
        self._stop_event = threading.Event()
        self._joysticks = {}
        self._keys = set()

    def stop(self):
        self._stop_event.set()

    def run(self):
        pygame.init()
        pygame.joystick.init()
        pygame.display.set_mode((240, 80))
        pygame.display.set_caption("ROV input")
        for index in range(pygame.joystick.get_count()):
            self._add_joystick(index)
        next_tick = time.monotonic()
        while not self._stop_event.is_set():
            self._handle_events()
            self.bus.publish("input.state", self._snapshot())
            next_tick += self.period
            delay = next_tick - time.monotonic()
            if delay > 0:
                time.sleep(delay)
            else:
                next_tick = time.monotonic()
        pygame.quit()

    def _add_joystick(self, index):
        try:
            joy = pygame.joystick.Joystick(index)
        except pygame.error:
            log.exception("Could not open controller %s", index)
            return
        if joy.get_instance_id() in self._joysticks:
            return
        self._joysticks[joy.get_instance_id()] = joy
        log.info("Controller connected: %s", joy.get_name())
        self.bus.publish("input.device", {"event": "connected", "name": joy.get_name()})

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._stop_event.set()
            elif event.type in (pygame.KEYDOWN, pygame.KEYUP):
                name = pygame.key.name(event.key)
                down = event.type == pygame.KEYDOWN
                if down:
                    self._keys.add(name)
                else:
                    self._keys.discard(name)
                self.bus.publish("input.key", {"key": name, "down": down})
            elif event.type == pygame.JOYDEVICEADDED:
                self._add_joystick(event.device_index)
            elif event.type == pygame.JOYDEVICEREMOVED:
                joy = self._joysticks.pop(event.instance_id, None)
                if joy is not None:
                    log.warning("Controller disconnected")
                    self.bus.publish("input.device", {"event": "disconnected"})

    def _snapshot(self):
        controllers = {}
        for instance_id, joy in list(self._joysticks.items()):
            try:
                controllers[instance_id] = {
                    "axes": [
                        apply_deadzone(joy.get_axis(i), self.dead_zone)
                        for i in range(joy.get_numaxes())
                    ],
                    "buttons": [joy.get_button(i) for i in range(joy.get_numbuttons())],
                    "hats": [joy.get_hat(i) for i in range(joy.get_numhats())],
                }
            except pygame.error:
                self._joysticks.pop(instance_id, None)
        return {"controllers": controllers, "keys": sorted(self._keys)}