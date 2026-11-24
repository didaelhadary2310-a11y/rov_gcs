from rov_gcs.core.event_bus import EventBus
from rov_gcs.input.input_thread import InputThread
from rov_gcs.input.profiles import ProfileManager, save_profile


def test_profile_changes_deadzone_without_restart(tmp_path):
    save_profile("precise", {"controller": "", "dead_zone": 0.3}, tmp_path)
    save_profile("loose", {"controller": "", "dead_zone": 0.05}, tmp_path)
    bus = EventBus()
    ProfileManager(bus, tmp_path)
    thread = InputThread(bus, 50, 0.1)

    bus.publish("profile.load", "precise")
    assert thread.dead_zone == 0.3

    bus.publish("profile.load", "loose")
    assert thread.dead_zone == 0.05