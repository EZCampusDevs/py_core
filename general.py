"""General computation code."""

from . import constants


def encode_days_of_week(data: dict[str, bool]) -> int:
    """Encodes standard dictionary of days to integer representation.

    Examples:
        >>> encode_days_of_week({"monday": False, "tuesday": False, "wednesday": False, "thursday": False, "friday": False, "saturday": False, "sunday": False})
        0
        >>> encode_days_of_week({"monday": True, "tuesday": False, "wednesday": False, "thursday": False, "friday": False, "saturday": False, "sunday": False})
        1
        >>> encode_days_of_week({"monday": False, "tuesday": True, "wednesday": False, "thursday": False, "friday": False, "saturday": False, "sunday": False})
        2
        >>> encode_days_of_week({"monday": False, "tuesday": False, "wednesday": True, "thursday": False, "friday": False, "saturday": False, "sunday": False})
        4
        >>> encode_days_of_week({"monday": False, "tuesday": False, "wednesday": False, "thursday": False, "friday": False, "saturday": False, "sunday": True})
        64
        >>> encode_days_of_week({"monday": True, "tuesday": True, "wednesday": False, "thursday": False, "friday": False, "saturday": False, "sunday": False})
        3
        >>> encode_days_of_week({"monday": True, "tuesday": True, "wednesday": True, "thursday": True, "friday": True, "saturday": True, "sunday": True})
        127
    """
    value = 0
    if data.get("monday", False):
        value |= constants.MONDAY
    if data.get("tuesday", False):
        value |= constants.TUESDAY
    if data.get("wednesday", False):
        value |= constants.WEDNESDAY
    if data.get("thursday", False):
        value |= constants.THURSDAY
    if data.get("friday", False):
        value |= constants.FRIDAY
    if data.get("saturday", False):
        value |= constants.SATURDAY
    if data.get("sunday", False):
        value |= constants.SUNDAY
    return value


def decode_days_of_week(value) -> dict[str, bool]:
    """Decodes integer representation of days to standard dictionary.

    Examples:
        >>> decode_days_of_week(0)
        {'monday': False, 'tuesday': False, 'wednesday': False, 'thursday': False, 'friday': False, 'saturday': False, 'sunday': False}
        >>> decode_days_of_week(1)
        {'monday': True, 'tuesday': False, 'wednesday': False, 'thursday': False, 'friday': False, 'saturday': False, 'sunday': False}
        >>> decode_days_of_week(2)
        {'monday': False, 'tuesday': True, 'wednesday': False, 'thursday': False, 'friday': False, 'saturday': False, 'sunday': False}
        >>> decode_days_of_week(4)
        {'monday': False, 'tuesday': False, 'wednesday': True, 'thursday': False, 'friday': False, 'saturday': False, 'sunday': False}
        >>> decode_days_of_week(64)
        {'monday': False, 'tuesday': False, 'wednesday': False, 'thursday': False, 'friday': False, 'saturday': False, 'sunday': True}
        >>> decode_days_of_week(3)
        {'monday': True, 'tuesday': True, 'wednesday': False, 'thursday': False, 'friday': False, 'saturday': False, 'sunday': False}
        >>> decode_days_of_week(127)
        {'monday': True, 'tuesday': True, 'wednesday': True, 'thursday': True, 'friday': True, 'saturday': True, 'sunday': True}
    """
    return {
        "monday": bool(value & constants.MONDAY),
        "tuesday": bool(value & constants.TUESDAY),
        "wednesday": bool(value & constants.WEDNESDAY),
        "thursday": bool(value & constants.THURSDAY),
        "friday": bool(value & constants.FRIDAY),
        "saturday": bool(value & constants.SATURDAY),
        "sunday": bool(value & constants.SUNDAY)
    }
