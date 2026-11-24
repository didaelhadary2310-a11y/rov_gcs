from rov_gcs.core.event_bus import EventBus


def test_publish_reaches_subscriber():
    bus = EventBus()
    got = []
    bus.subscribe("x", got.append)
    bus.publish("x", 5)
    assert got == [5]