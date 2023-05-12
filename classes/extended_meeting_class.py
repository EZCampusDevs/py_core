"""ExpandedMeeting class module.

The ExpandedMeetingLogical class and by extension the module's functions represent universal custom calendar event
structures and data values.
"""

from pydantic import root_validator, validator

from .meeting_class import Meeting
from ..general_validators import is_valid_hexadecimal_colour


class ExtendedMeeting(Meeting):
    """Event class defines a general calendar event.

    name: Nane of the event.
    class_time: List of Meeting objects. (meeting_class.py).
    seats_filled: Number of seats filled.
        seats_filled >= 0.
    max_capacity: Maximum capacity of attendees.
        max_capacity = -1 means infinite capacity.
        max_capacity >= -1 and != 0.
        max_capacity >= seats_filled.
    is_virtual: Defines if the class is completely virtual/online.
    """
    # time_start: time -> Meeting attribute.
    # time_end: time -> Meeting attribute.
    # days_of_week: int -> Meeting attribute.
    # date_start: date -> Meeting attribute.
    # date_end: date -> Meeting attribute.
    # repeat_timedelta_days: int -> Meeting attribute.
    # location: str -> Meeting attribute.
    name: str
    description: str
    seats_filled: int
    max_capacity: int
    is_virtual: bool
    colour: str | None

    @root_validator()
    def verify_valid_seats_capacity_values(cls, values):
        seats_filled = values.get("seats_filled")
        max_capacity = values.get("max_capacity")
        if not (seats_filled >= 0):
            raise ValueError("Expected seats_filled >= 0")
        if not (max_capacity >= -1) or max_capacity == 0:
            raise ValueError("Expected max_capacity >= -1 and != 0")
        # if max_capacity != -1 and (seats_filled > max_capacity):
        #     raise ValueError("seats_filled has passed the max_capacity")
        # TODO(Daniel): This is commented out for now. There are instances of courses where people are allowed to be
        #  registered even though it is past the maximum capacity.
        return values

    @validator("colour")
    def verify_hexadecimal_colour_code(cls, v):
        if not is_valid_hexadecimal_colour(v):
            raise ValueError("Invalid hexadecimal colour code")
        return v


def extended_meeting_to_simplified_json(extended_meeting: ExtendedMeeting) -> dict[str, int | str | None]:
    """Converts an ExtendedMeeting objects to a simplified json list.

    Args:
        extended_meeting: ExtendedMeeting object.

    Returns:
        json dict of the ExtendedMeeting.
    """
    return {
        "title": f"{extended_meeting.name}",
        "description": f"{extended_meeting.description}\n"
                       f"Is virtual: {extended_meeting.is_virtual}\n"
                       f"Seats filled: {extended_meeting.seats_filled}\n"
                       f"Max capacity: {extended_meeting.max_capacity}\n",
        "time_start": extended_meeting.time_start.isoformat(),
        "time_end": extended_meeting.time_end.isoformat(),
        "days_of_week": extended_meeting.days_of_week,
        "date_start": extended_meeting.get_actual_date_start().isoformat(),
        "date_end": extended_meeting.get_actual_date_end().isoformat(),
        # Unlike the format using by the backend logic, it is sending the simplified actual date starts and ends.
        "repeat_timedelta_days": extended_meeting.repeat_timedelta_days,
        "location": extended_meeting.location,
        "colour": extended_meeting.colour
    }
