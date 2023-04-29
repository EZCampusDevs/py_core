"""Faculty class module.

The Faculty class and by extension the module's functions represent universal faculty structures and data values.
"""

from typing import Optional

from pydantic import BaseModel


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
