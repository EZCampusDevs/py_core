"""General computation code."""

from . import constants


def decode_days_of_week(value) -> dict[str, bool]:
    return {
        "monday": bool(value & constants.MONDAY),
        "tuesday": bool(value & constants.TUESDAY),
        "wednesday": bool(value & constants.WEDNESDAY),
        "thursday": bool(value & constants.THURSDAY),
        "friday": bool(value & constants.FRIDAY),
        "saturday": bool(value & constants.SATURDAY),
        "sunday": bool(value & constants.SUNDAY)
    }
