from rov_gcs.input.profiles import (
    ProfileManager,
    save_profile,
    load_profile,
    list_profiles,
    find_profile_for_controller,
)


class FakeBus:
    def __init__(self):
        self.handlers = {}
        self.published = []

    def subscribe(self, topic, handler):
        self.handlers[topic] = handler

    def publish(self, topic, data=None):
        self.published.append((topic, data))


def test_save_and_load(tmp_path):
    data = {"controller": "xbox", "axes": {"0": "yaw"}}
    save_profile("pilot", data, tmp_path)
    assert load_profile("pilot", tmp_path) == data


def test_list_profiles(tmp_path):
    save_profile("b", {}, tmp_path)
    save_profile("a", {}, tmp_path)
    assert list_profiles(tmp_path) == ["a", "b"]


def test_find_profile_for_controller(tmp_path):
    save_profile("pilot", {"controller": "xbox"}, tmp_path)
    assert find_profile_for_controller("Xbox 360 Controller", tmp_path) == "pilot"


def test_unknown_controller_gets_default(tmp_path):
    save_profile("pilot", {"controller": "xbox"}, tmp_path)
    assert find_profile_for_controller("Logitech F310", tmp_path) == "default"


def test_manager_loads_profile_when_controller_connects(tmp_path):
    save_profile("pilot", {"controller": "xbox"}, tmp_path)
    bus = FakeBus()
    manager = ProfileManager(bus, tmp_path)
    bus.handlers["input.device"]({"event": "connected", "name": "Xbox 360 Controller"})
    assert manager.active == "pilot"
    assert bus.published[-1][0] == "profile.applied"


def test_manager_survives_missing_profile(tmp_path):
    bus = FakeBus()
    manager = ProfileManager(bus, tmp_path)
    bus.handlers["profile.load"]("does_not_exist")
    assert manager.active is None