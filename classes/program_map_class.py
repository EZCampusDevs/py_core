"""ProgramMap defines standard class structure for university programs."""

import json
from types import SimpleNamespace
from typing import Optional

from pydantic import BaseModel, root_validator

from ..constants import CUMULATIVE_PROGRAM_MAP_KEY_WORD


class ProgramMap(BaseModel):
    """Program map class.

    Examples:
        >>> ProgramMap( \
                is_abstracted=False, \
                school_short_name="OTLS", \
                name="Mechatronics Engineering (2021 Entry and later)", \
                manifest_list=["MATH2070U", "MECE2420U", "MECE2430U",  \
                              "METE2020U", "METE2030U", "STAT2800U"], \
                year=2, \
                semester=2, \
                semester_keyword="Winter", \
                semester_count=4, \
                total_years=4, \
                total_semesters_count=8, \
                category="Engineering", \
                description="example_description" \
            )
        ProgramMap(is_abstracted=False, school_short_name='OTLS', name='Mechatronics Engineering (2021 Entry and later)', manifest_list=['MATH2070U', 'MECE2420U', 'MECE2430U', 'METE2020U', 'METE2030U', 'STAT2800U'], year=2, semester=2, semester_keyword='Winter', semester_count=4, total_years=4, total_semesters_count=8, category='Engineering', description='example_description')
        >>> ProgramMap( \
                is_abstracted=True, \
                school_short_name="PAIN", \
                name="Best Engineering", \
                manifest_list=["Mechatronics Y2S1", "Mechatronics Y2S2"], \
                semester_keyword="Fall, Winter", \
                category=f"({CUMULATIVE_PROGRAM_MAP_KEY_WORD}) Engineering", \
                description="example_description" \
            )
        ProgramMap(is_abstracted=True, school_short_name='PAIN', name='Best Engineering', manifest_list=['Mechatronics Y2S1', 'Mechatronics Y2S2'], year=None, semester=None, semester_keyword='Fall, Winter', semester_count=None, total_years=None, total_semesters_count=None, category='(CUMULATIVE) Engineering', description='example_description')
    """

    is_abstracted: bool
    school_short_name: str
    name: str
    manifest_list: list[str]  # List of pmap.names for is_abstracted, else list of course codes.
    year: Optional[int]  # Probably None for is_abstracted.
    semester: Optional[int]  # Probably None for is_abstracted.
    semester_keyword: str
    semester_count: Optional[int]  # Probably None for is_abstracted.
    total_years: Optional[int]  # Probably None for is_abstracted.
    total_semesters_count: Optional[int]  # Probably None for is_abstracted.
    category: str
    description: str

    @root_validator()
    def verify_valid_int_values(cls, values):
        year = values.get("year")
        semester = values.get("semester")
        semester_count = values.get("semester_count")
        total_years = values.get("total_years")
        total_semesters_count = values.get("total_semesters_count")
        if not values.get("is_abstracted"):  # Not is_abstracted.
            if year < 0:
                raise ValueError(f"Expected year={year} >= 0")
            if semester < 0 or semester > 2:
                raise ValueError(f"Expected 0 <= semester={semester} <= 2")
            if semester_count < 0:
                raise ValueError(f"Expected semester_count={semester_count} >= 0")
            if total_years < 0:
                raise ValueError(f"Expected total_years={total_years} >= 0")
            if total_semesters_count < 0:
                raise ValueError(f"Expected total_semesters_count={total_semesters_count} >= 0")
            if year > total_years:
                raise ValueError(f"Expected year={year} <= total_years={total_years}")
            if semester_count > total_semesters_count:
                raise ValueError(
                    f"Expected semester_count={semester_count} <= total_semesters_count="
                    f"{total_semesters_count}"
                )
            if semester > semester_count:
                raise ValueError(f"Expected semester={semester} <= semester_count={semester_count}")
        else:  # is_abstracted.
            category = values.get("category")
            if CUMULATIVE_PROGRAM_MAP_KEY_WORD not in category:
                raise ValueError(f'Expected "{CUMULATIVE_PROGRAM_MAP_KEY_WORD}" to be in category')
        return values

    def is_cumulative(self) -> bool:
        """Determines if a program map is cumulative based object str data.

        Returns:
            True if the program map is considered cumulative.
        """
        if self.is_abstracted and CUMULATIVE_PROGRAM_MAP_KEY_WORD in self.category:
            return True
        return False

    def to_json(self) -> str:
        """Converts a SemesterConfig object to json str.

        Returns:
            json string of the SemesterConfig object.
        """

        def default(obj):
            return obj.__dict__

        return json.dumps(self, default=default, indent=4)

    @staticmethod
    def from_json(json_str: str):  # -> ProgramMap:
        """Converts json str to a ProgramMap object.

        Returns:
            json string of the ProgramMap object.
        """
        simple = json.loads(json_str, object_hook=lambda d: SimpleNamespace(**d))

        return ProgramMap(
            is_abstracted=simple.is_abstracted,
            school_short_name=simple.school_short_name,
            name=simple.name,
            manifest_list=simple.manifest_list,
            year=simple.year if '"year"' in json_str else None,
            semester=simple.semester if '"semester"' in json_str else None,
            semester_keyword=simple.semester_keyword if '"semester_keyword"' in json_str else None,
            semester_count=simple.semester_count if '"semester_count"' in json_str else None,
            total_years=simple.total_years if '"total_years"' in json_str else None,
            total_semesters_count=simple.total_semesters_count
            if '"total_semesters_count"' in json_str
            else None,
            category=simple.category,
            description=simple.description,
        )


def decode_program_map_from_json(json_file_path: str) -> ProgramMap:
    """Acts as a decoder from a json config file to a ProgramMap object.

    Warnings:
        Potential FileNotFoundError raises!

    Args:
        json_file_path: Filepath of the json program map file.

    Returns:
        A ProgramMap object with the dumped/decoded information from the given filepath.
    """
    with open(json_file_path) as json_config_file:
        json_str = json_config_file.read()
    return ProgramMap.from_json(json_str)
