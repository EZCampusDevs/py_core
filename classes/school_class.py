# Copyright (C) 2022-2023 EZCampus 
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
