def apply_deadzone(value, dead_zone):
    if abs(value) < dead_zone:
        return 0.0
    sign = 1.0 if value > 0 else -1.0
    return sign * (abs(value) - dead_zone) / (1.0 - dead_zone)