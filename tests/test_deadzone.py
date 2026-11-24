from rov_gcs.input.deadzone import apply_deadzone


def test_small_values_are_zeroed():
    assert apply_deadzone(0.05, 0.1) == 0.0


def test_full_value_stays_full():
    assert apply_deadzone(1.0, 0.1) == 1.0