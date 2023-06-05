"""Instructor class module.

The Instructor class and by extension the module's functions represent universal faculty structures and data values.
"""

import re
from typing import Optional

from pydantic import BaseModel, validator


class Instructor(BaseModel):
    """Instructor class defines a single faculty instructor.

    Examples:
        >>> Instructor(faculty_id=1, name="Jeon, Daniel", email="daniel.jeon@domain.com", rating=50)
        Instructor(faculty_id=1, name='Jeon, Daniel', email='daniel.jeon@domain.com', rating=50)
        >>> Instructor(faculty_id=1)
        Instructor(faculty_id=1, name=None, email=None, rating=None)
    """

    faculty_id: int
    name: Optional[str]
    email: Optional[str]
    rating: Optional[int]

    @validator("rating")
    def verify_valid_rating(cls, v):
        if v is not None and not isinstance(v, int):
            raise ValueError(f"Expected type <None> or <int>, got {type(v)}")
        if isinstance(v, int) and not (0 <= v <= 100):
            raise ValueError(f"With <int> expected 0 <= rating <= 100, got rating={v}")
        return v

    @validator("name")
    def instructor_name_cleanup(cls, v):
        return name_cleanup(v)


def name_cleanup(source_name: str) -> str:
    """Cleanup of str for instructor name.

    Args:
        source_name: Original instructor name str.

    Returns:
        Cleaned up instructor name str.

    Examples:
        >>> name_cleanup(source_name="!@#ABCde f123'.-_")
        'abcdef'
    """
    if isinstance(source_name, str):
        # Ensure only lowercase alphabetical characters.
        return "".join(re.findall("[a-z]", source_name.lower()))
