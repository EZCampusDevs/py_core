"""School defines standard class structure for different educational institutions."""

from datetime import tzinfo

from pydantic import BaseModel
from pydantic import validator
from pytz import timezone, all_timezones


class School(BaseModel):
    """School class, standardized single object to represent educational institutions.

    Args:
        name (str): School name, must be unique.
        timezone_str (str): IANA standard timezone string.
    """

    name: str
    timezone_str: str = "UTC"

    @validator("timezone_str")
    def verify_timezone_str(cls, v):
        if v not in all_timezones:
            raise ValueError(
                f"timezone_str={v} is not allowed. Allowed units defined by: pytz.all_timezones"
            )
        return v

    def get_timezone(self) -> tzinfo:
        return timezone(self.timezone_str)
