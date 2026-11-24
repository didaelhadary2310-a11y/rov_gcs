import logging
import threading
from collections import defaultdict

log = logging.getLogger(__name__)


class EventBus:
    """Thread-safe publish-subscribe bus."""

    def __init__(self):
        self._subs = defaultdict(list)
        self._lock = threading.Lock()

    def subscribe(self, topic, callback):
        with self._lock:
            self._subs[topic].append(callback)

    def unsubscribe(self, topic, callback):
        with self._lock:
            if callback in self._subs[topic]:
                self._subs[topic].remove(callback)

    def publish(self, topic, data=None):
        with self._lock:
            callbacks = list(self._subs[topic])
        for callback in callbacks:
            try:
                callback(data)
            except Exception:
                log.exception("Handler failed for topic %s", topic)