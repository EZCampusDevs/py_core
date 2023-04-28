"""Calendar class module.

The Calendar classes represent universal custom calendar event structures and data values.
"""

from typing import Optional

from pydantic import BaseModel, root_validator

from .extended_meeting_class import ExtendedMeeting, extended_meeting_to_simplified_json
from ..general_validators import is_valid_hexadecimal_colour


class CalendarLogical(BaseModel):
    uuid: str
    author: str
    name: str
    category: str
    description: str
    is_public: bool
    subscriber_count: int
    subscribe_capacity: int
    calendar_tag: str
    meetings: list[ExtendedMeeting]
    colour: str | None

    @root_validator()
    def verify_hexadecimal_colour_code(cls, values):
        colour = values.get("colour")
        if not is_valid_hexadecimal_colour(colour):
            raise ValueError("Invalid hexadecimal colour code")
        return values


class CalendarCreation(BaseModel):
    # uuid: str used for internal logic not part of request body.
    # author: str is not needed for creation (automatic).
    name: str
    category: str = ""
    description: str = ""
    is_public: bool = False
    subscribe_capacity: int = -1  # -1 means infinity.
    colour: Optional[str]


class CalendarEdit(BaseModel):
    # uuid: str used for internal logic not part of request body.
    author: Optional[str]
    name: Optional[str]
    category: Optional[str]
    description: Optional[str]
    is_public: Optional[bool]
    subscribe_capacity: Optional[int]
    colour: Optional[str]

    @root_validator()
    def verify_hexadecimal_colour_code(cls, values):
        colour = values.get("colour")
        if not is_valid_hexadecimal_colour(colour):
            raise ValueError("Invalid hexadecimal colour code")
        return values


def calendars_to_simplified_json(calendar_list: list[CalendarLogical]) -> list[dict]:
    """Converts a list of CalendarLogical objects (calendar) to a simplified json list.

    Args:
        calendar_list: List of LogicalCalendar objects.

    Returns:
        json list of dicts of the calendar.
    """
    calendar_json_list = []
    for calendar in calendar_list:
        new_event = {
            "title": f"{calendar.name}",
            "description": f"{calendar.description}",
            "is_public": calendar.is_public,
            "category": f"{calendar.category}",
            "meetings": [extended_meeting_to_simplified_json(ex_mt) for ex_mt in calendar.meetings]
        }
        calendar_json_list.append(new_event)
    return calendar_json_list
