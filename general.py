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


def decode_days_of_week(value: None | int) -> None | dict[str, bool]:
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
        >>> decode_days_of_week(None)
    """
    if value is None:
        return None
    return {
        "monday": bool(value & constants.MONDAY),
        "tuesday": bool(value & constants.TUESDAY),
        "wednesday": bool(value & constants.WEDNESDAY),
        "thursday": bool(value & constants.THURSDAY),
        "friday": bool(value & constants.FRIDAY),
        "saturday": bool(value & constants.SATURDAY),
        "sunday": bool(value & constants.SUNDAY),
    }


def encode_weekday_ints(data: list[int]) -> int:
    """Encodes list of weekday ints to integer representation.

    Examples:
        >>> encode_weekday_ints([])
        0
        >>> encode_weekday_ints([0])
        1
        >>> encode_weekday_ints([1])
        2
        >>> encode_weekday_ints([2])
        4
        >>> encode_weekday_ints([6])
        64
        >>> encode_weekday_ints([0, 1])
        3
        >>> encode_weekday_ints([0, 1, 2, 3, 4, 5, 6])
        127
    """
    value = 0
    if 0 in data:
        value |= constants.MONDAY
    if 1 in data:
        value |= constants.TUESDAY
    if 2 in data:
        value |= constants.WEDNESDAY
    if 3 in data:
        value |= constants.THURSDAY
    if 4 in data:
        value |= constants.FRIDAY
    if 5 in data:
        value |= constants.SATURDAY
    if 6 in data:
        value |= constants.SUNDAY
    return value


def decode_weekday_ints(value: None | int) -> None | list[int]:
    """Decode integer representation of days to list of weekday ints.

    Examples:
        >>> decode_weekday_ints(0)
        []
        >>> decode_weekday_ints(1)
        [0]
        >>> decode_weekday_ints(2)
        [1]
        >>> decode_weekday_ints(4)
        [2]
        >>> decode_weekday_ints(64)
        [6]
        >>> decode_weekday_ints(3)
        [0, 1]
        >>> decode_weekday_ints(127)
        [0, 1, 2, 3, 4, 5, 6]
        >>> decode_weekday_ints(None)
    """
    if value is None:
        return None
    data_list = []
    if value & constants.MONDAY:
        data_list.append(0)
    if value & constants.TUESDAY:
        data_list.append(1)
    if value & constants.WEDNESDAY:
        data_list.append(2)
    if value & constants.THURSDAY:
        data_list.append(3)
    if value & constants.FRIDAY:
        data_list.append(4)
    if value & constants.SATURDAY:
        data_list.append(5)
    if value & constants.SUNDAY:
        data_list.append(6)
    return data_list
