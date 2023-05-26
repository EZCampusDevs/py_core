"""User model pydantic schemas.

Notes:
    Ideally (logically required technically):
        school_short_name = School.short_name
        program = ProgramMap.name or ProgramMap.category.
"""

import base64
import hashlib
import re
from datetime import datetime
from typing import Optional
from uuid import uuid4

import bcrypt
from fastapi import HTTPException, status
from pydantic import BaseModel, validator, root_validator

from ..constants import USERNAME_MIN_LEN, USERNAME_MAX_LEN, EMAIL_MIN_LEN, EMAIL_MAX_LEN, PASS_MIN_LEN, PASS_MAX_LEN, \
    NAME_MIN_LEN, NAME_MAX_LEN, DESC_MAX_LEN, PROGRAM_MAX_LEN, YEAR_OF_STUDY_MIN, YEAR_OF_STUDY_MAX

API_406_USERNAME_INVALID = HTTPException(
    status_code=status.HTTP_406_NOT_ACCEPTABLE,
    detail=f"Usernames must be [{USERNAME_MIN_LEN} to {USERNAME_MAX_LEN}] characters and can only contain lowercase "
           f"alphanumerics, '.' and '_'."
)
API_406_EMAIL_INVALID = HTTPException(
    status_code=status.HTTP_406_NOT_ACCEPTABLE,
    detail="Email must be a valid format."
)
API_406_PASSWORD_INVALID = HTTPException(
    status_code=status.HTTP_406_NOT_ACCEPTABLE,
    detail=f"Passwords must be [{PASS_MIN_LEN} to {NAME_MAX_LEN}] characters."
)
API_406_USERNAME_PASSWORD_MATCH = HTTPException(
    status_code=status.HTTP_406_NOT_ACCEPTABLE,
    detail="Seriously? Using your username as your password? No."
)
API_406_NAME_INVALID = HTTPException(
    status_code=status.HTTP_406_NOT_ACCEPTABLE,
    detail=f"Names must be [{NAME_MIN_LEN} to {NAME_MAX_LEN}] characters."
)
API_406_DESCRIPTION_INVALID = HTTPException(
    status_code=status.HTTP_406_NOT_ACCEPTABLE,
    detail=f"Descriptions must be less than ({DESC_MAX_LEN}) characters."
)
API_406_PROGRAM_INVALID = HTTPException(
    status_code=status.HTTP_406_NOT_ACCEPTABLE,
    detail=f"Programs must be less than ({PROGRAM_MAX_LEN}) characters."
)
API_406_YEAR_OF_STUDY_INVALID = HTTPException(
    status_code=status.HTTP_406_NOT_ACCEPTABLE,
    detail=f"Year of study must be [{YEAR_OF_STUDY_MIN} to {YEAR_OF_STUDY_MAX}]."
)
HTTP_409_BAD_ACCOUNT_STATUS = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Broken account status."
)


# ---------- Start of Validation Functions ----------
def valid_username(username: str) -> bool:
    """Check username type, characters and length.

    Args:
        username: Username string.

    Returns:
        True for valid, False for invalid.
    """
    if not isinstance(username, str) or len(username) < USERNAME_MIN_LEN or len(username) > USERNAME_MAX_LEN:
        return False
    return re.compile(r"^[a-z0-9_.]+$").match(username) is not None


def valid_email(email: str) -> bool:
    """Check if email is valid.

     Ensure valid type & length (Email & Password field have same # of
     available chars)

    Args:
        email: Email address

    Returns:
        Boolean defining a True = valid email, False = invalid email.
    """
    if not isinstance(email, str) or len(email) > EMAIL_MAX_LEN or len(email) < EMAIL_MIN_LEN:
        return False
    """
    Regular Expression validate email strings:

    >> username of email | a-z, A-Z, 0,9
    >> followed by an '@'
    >> followed by another a-z, A-Z, 0,9 string (the domain name)
    >> followed by a dot '.' , then a 2-n length string of a-z || A-Z 
        (com,ca,cz,de,ru) (the DNS)

    username@domain.dns
    """
    validate_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    if not re.fullmatch(validate_email, email):
        return False
    return True


def valid_password(password: str) -> bool:
    if not isinstance(password, str) or len(password) > PASS_MAX_LEN or len(password) < PASS_MIN_LEN:
        return False
    return True


def valid_hashed_password(password: str) -> bool:
    if not isinstance(password, str):
        return False
    return True


def hash_password(password: str) -> str:
    if isinstance(password, str):
        password.encode()  # Taken from the bcrypt docs (Work around for 72 char limit)
    return bcrypt.hashpw(
        base64.b64encode(hashlib.sha256(password.encode()).digest()),
        bcrypt.gensalt(12)
    ).decode()


def valid_name(name: str) -> bool:
    if not isinstance(name, str) or len(name) < NAME_MIN_LEN or len(name) > NAME_MAX_LEN:
        return False
    return True


def valid_description(description: str) -> bool:
    if not isinstance(description, str) or len(description) > DESC_MAX_LEN:
        return False
    return True


# TODO: Warning! No school_short_name validation!


def valid_program(program: str) -> bool:
    if not isinstance(program, str) or len(program) > PROGRAM_MAX_LEN:
        return False
    return True


def valid_year_of_study(year_of_study: str) -> bool:
    if not isinstance(year_of_study, int) or year_of_study < YEAR_OF_STUDY_MIN or year_of_study > YEAR_OF_STUDY_MAX:
        return False
    return True


def convert_account_status_to_str(account_status: int) -> str | None:
    # If account_status >= search able and usable account:
    match account_status:
        case -9:
            return "Deleted"
        case -8:
            return "Banned"
        case 0:
            return "Standard Okay"
        case 3:
            return "Club Executive"
        case 4:
            return "Society Executive"
        case 5:
            return "Privileged User"
        case 8:
            return "Admin"
        case 9:
            return "Developer"
        case _:
            return None


# ---------- End of Validation Functions ----------


class CreateUser(BaseModel):
    """Model used for creating a new user.

    Examples:
        >>> CreateUser( \
                username="borkd", \
                email="coding@waytoolate.com", \
                password="admin123", \
                name="Daniel Jeon", \
                description="Hello there!", \
                school_short_name="OTSL", \
                program="Engineering", \
                year_of_study=2, \
                private_account=0 \
        )
        CreateUser(username='borkd', email='coding@waytoolate.com', password='$HASHED_PASSWORD_HERE$', name='Daniel Jeon', description='Hello there!', school_short_name='OTSL', program='Engineering', year_of_study=2, private_account=False, is_verified=0, account_status=0, schedule_tag='UUID4_STR_HERE')
        >>> CreateUser( \
                username="minimum_test_case", \
                email="email@domain.com", \
                password="password123", \
        )
        CreateUser(username='minimum_test_case', email='email@domain.com', password='$HASHED_PASSWORD_HERE$', name='test_username', description='', school_short_name=None, program=None, year_of_study=None, private_account=True, is_verified=0, account_status=0, schedule_tag='UUID4_STR_HERE')
    """
    username: str
    email: str
    password: str
    name: Optional[str]  # If name is not entered it is defaulted later by pydantic name validator.
    description: Optional[str]
    school_short_name: Optional[str]
    program: Optional[str]
    year_of_study: int = 0
    private_account: bool = True
    is_verified = 0  # Force the default of value 0.
    account_status: int = 0  # Default of value 0.
    schedule_tag = str(uuid4())  # Force the default of random UUID4 value.

    @validator("username")
    def validate_username(cls, v):
        if not valid_username(v):
            raise API_406_USERNAME_INVALID
        return v

    @validator("email")
    def validate_email(cls, v):
        if not valid_email(v):
            raise API_406_EMAIL_INVALID
        return v

    @validator("password")
    def validate_password(cls, v):
        if not valid_password(v):
            raise API_406_PASSWORD_INVALID
        return hash_password(v)  # Hash the plaintext password.

    @root_validator()
    def validate_username_and_password(cls, values):
        username = values.get("username")
        password = values.get("password")
        if username == password:
            raise API_406_USERNAME_PASSWORD_MATCH
        return values

    @validator("name", always=True)  # https://stackoverflow.com/a/71001357
    def validate_name(cls, v, values):
        if not isinstance(v, str):
            return v or values["username"]  # Default name to match username if name is unspecified.
        elif isinstance(v, str) and not valid_name(v):
            raise API_406_NAME_INVALID
        return v

    @validator("description")
    def validate_description(cls, v):
        if not valid_description(v):
            raise API_406_DESCRIPTION_INVALID
        return v

    @validator("program")
    def validate_program(cls, v):
        if not valid_program(v):
            raise API_406_PROGRAM_INVALID
        return v

    @validator("year_of_study")
    def validate_year_of_study(cls, v):
        if not valid_year_of_study(v):
            raise API_406_YEAR_OF_STUDY_INVALID
        return v

    @validator("account_status")
    def validate_account_status(cls, v):
        if not isinstance(convert_account_status_to_str(v), str):
            raise HTTP_409_BAD_ACCOUNT_STATUS
        return v


class EditUser(BaseModel):
    """Model used for editing user values."""
    username: str
    email: str
    password: str
    name: str
    description: Optional[str]
    school_short_name: Optional[str]
    program: Optional[str]
    year_of_study: Optional[int]
    private_account: bool
    is_verified: bool
    account_status: int
    schedule_tag: str

    @validator("username")
    def validate_username(cls, v):
        if not valid_username(v):
            raise API_406_USERNAME_INVALID
        return v

    @validator("email")
    def validate_email(cls, v):
        if not valid_email(v):
            raise API_406_EMAIL_INVALID
        return v

    @validator("password")
    def validate_password(cls, v):
        if not valid_password(v):
            raise API_406_PASSWORD_INVALID
        return hash_password(v)  # Hash the plaintext password.

    @root_validator()
    def validate_username_and_password(cls, values):
        username = values.get("username")
        password = values.get("password")
        if username == password:
            raise API_406_USERNAME_PASSWORD_MATCH
        return values

    @validator("name")
    def validate_name(cls, v):
        if not valid_name(v):
            raise API_406_NAME_INVALID
        return v

    @validator("description")
    def validate_description(cls, v):
        if not valid_description(v):
            raise API_406_DESCRIPTION_INVALID
        return v

    @validator("program")
    def validate_program(cls, v):
        if not valid_program(v):
            raise API_406_PROGRAM_INVALID
        return v

    @validator("year_of_study")
    def validate_year_of_study(cls, v):
        if not valid_year_of_study(v):
            raise API_406_YEAR_OF_STUDY_INVALID
        return v


class BasicUser(BaseModel):
    """Model used for internal logic."""
    username: str
    email: str
    hashed_password: str
    name: str
    description: Optional[str]
    school_short_name: Optional[str]
    program: Optional[str]
    year_of_study: Optional[int]
    private_account: bool
    is_verified: bool
    account_status: int
    schedule_tag: str
    metadata_created_on: datetime

    def get_account_status_str(self) -> str | None:
        return convert_account_status_to_str(self.account_status)

    def is_executive(self):
        return self.account_status >= 3

    def is_admin(self):
        return self.account_status >= 8


def edit_user_from_basic_user(basic_user: BasicUser, password: str) -> EditUser:
    """Get EditUser copy from BasicUser.

    Args:
        basic_user: BasicUser object.
        password: New password of the EditedUser.

    Notes:
        Warning! The basic user uses a hashed password. Translated EditUser will have this hashed password. The
        EditUser password should be updated after.

    Returns:
        Converted EditUser.
    """
    return EditUser(
        username=basic_user.username,
        email=basic_user.email,
        password=password,
        name=basic_user.name,
        description=basic_user.description,
        school_short_name=basic_user.school_short_name,
        program=basic_user.program,
        year_of_study=basic_user.year_of_study,
        private_account=basic_user.private_account,
        is_verified=basic_user.is_verified,
        account_status=basic_user.account_status,
        schedule_tag=basic_user.schedule_tag,
    )