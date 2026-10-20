"""DEPRECATED copy of an older fee formula. Do not use."""


def compute_late_fee(amount, days):  # type: ignore[no-untyped-def]
    if days <= 5:
        return 0
    return round(float(amount) * 0.02, 2)
