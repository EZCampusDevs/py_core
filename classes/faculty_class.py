"""Faculty class module.

The Faculty class and by extension the module's functions represent universal faculty structures and data values.
"""

from typing import Optional

from pydantic import BaseModel, validator


class Faculty(BaseModel):
    """Faculty class defines a single faculty instructor.

    Examples:
        >>> Faculty(faculty_id=1, name="Jeon, Daniel", email="daniel.jeon@domain.com", rating=50)
        Faculty(faculty_id=1, name='Jeon, Daniel', email='daniel.jeon@domain.com', rating=50)
        >>> Faculty(faculty_id=1)
        Faculty(faculty_id=1, name=None, email=None, rating=None)
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
