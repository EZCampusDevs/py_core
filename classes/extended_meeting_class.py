"""
ExpandedMeeting class module.

The ExpandedMeetingLogical class and by extension the module's functions represent universal custom
 calendar event structures and data values.
"""

from datetime import timedelta

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
        # TODO(Daniel): This is commented out for now. There are instances of courses where people
        #  are allowed to be registered even though it is past the maximum capacity.
        return values

    @validator("colour")
    def verify_hexadecimal_colour_code(cls, v):
        if v is not None and not is_valid_hexadecimal_colour(v):
            raise ValueError("Invalid hexadecimal colour code")
        return v

    def raw_new_line_description(self) -> str:
        return self.description.replace("\n", r"\n")

    def has_space(self) -> bool:
        """Determine if an ExtendedMeeting still has space for people to join.

        Returns:
            True if empty seats remain, else False.
        """
        if self.max_capacity == -1 or (self.max_capacity - self.seats_filled > 0):
            return True
        return False


def to_single_occurrences(ex_mt: ExtendedMeeting) -> list[ExtendedMeeting]:
    """Breaks reoccurring meeting into individual non-reoccurring (single occurrence) Meetings.

    Notes:
        This function is based off the same function in the Meeting class module.
    """
    if ex_mt.occurrence_unit is None:
        return [ex_mt]
    start_dates = ex_mt.all_start_dates()
    return [
        ExtendedMeeting(
            time_start=ex_mt.time_start,
            time_end=ex_mt.time_end,
            date_start=d,
            date_end=(d + timedelta(days=(ex_mt.date_end - ex_mt.date_start).days)),
            timezone_str=ex_mt.timezone_str,
            occurrence_unit=None,
            occurrence_interval=None,
            occurrence_limit=None,
            days_of_week=None,
            location=ex_mt.location,
            name=ex_mt.name,
            description=ex_mt.description,
            seats_filled=ex_mt.seats_filled,
            max_capacity=ex_mt.max_capacity,
            is_virtual=ex_mt.is_virtual,
            colour=ex_mt.colour,
        )
        for d in start_dates
    ]
