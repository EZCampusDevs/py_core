"""SemesterConfig defines standard class structure for different available program config modes.
"""

import json
import os
from datetime import date, time, datetime
from types import SimpleNamespace

from dotenv import load_dotenv
from pydantic import BaseModel, validator

load_dotenv()


class SemesterConfig(BaseModel):
    """Semester Config class, offers a standardized single object to represent all configs."""

    school_short_name: str  # Example: OTU.
    name: str  # Example: OTU Undergrad Fall 2022.
    description: str = ""
    semester: int
    semester_start: datetime
    semester_end: datetime
    course_api_ref: str
    course_api_params: dict

    @validator("semester")
    def validate_semester(cls, v):
        if v < 0 or v > 3:
            raise ValueError(f"Expected 0 <= semester={v} <= 3")
        return v

    def courses_table(self):
        return f"{os.getenv('SQL_CONFIG_COURSE_TABLE_PREFIX')}{self.name.lower().replace(' ', '_')}"

    def meetings_table(self):
        return (
            f"{os.getenv('SQL_CONFIG_COURSE_TABLE_PREFIX')}{self.name.lower().replace(' ', '_')}"
            f"{os.getenv('SQL_COURSE_MEETING_TABLE_SUFFIX')}"
        )

    def to_json(self) -> str:
        """Converts a SemesterConfig object to json str.

        Returns:
            json string of the SemesterConfig object.
        """

        def default(obj):
            if (
                isinstance(obj, date)
                or isinstance(obj, time)
                or isinstance(obj, datetime)
            ):
                return obj.isoformat()
            if isinstance(obj, int):
                return obj
            else:
                return obj.__dict__

        return json.dumps(self, default=default, indent=4)

    @staticmethod
    def from_json(json_str: str):  # -> SemesterConfig:
        """Converts a SemesterConfig object to json str.

        Returns:
            json string of the SemesterConfig object.
        """
        simple = json.loads(json_str, object_hook=lambda d: SimpleNamespace(**d))
        return SemesterConfig(
            school_short_name=simple.school_short_name,
            name=simple.name,
            description=simple.description,
            semester=simple.semester,
            semester_start=datetime.fromisoformat(simple.semester_start),
            semester_end=datetime.fromisoformat(simple.semester_end),
            course_api_ref=simple.course_api_ref,
            course_api_params=vars(
                simple.course_api_params
            ),  # vars() converts SimpleNamespace to dict.
        )


def decode_config_from_json(json_file_path: str) -> SemesterConfig:
    """Acts as a decoder from a json config file to a SemesterConfig object.

    Potential FileNotFoundError raises!

    Args:
        json_file_path: Filepath of the json config file

    Returns:
        A SemesterConfig object with the dumped/decoded information from the given filepath
    """
    with open(json_file_path) as json_config_file:
        json_str = json_config_file.read()
    return SemesterConfig.from_json(json_str)
