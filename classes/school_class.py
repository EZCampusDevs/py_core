"""School defines standard class structure for different educational institutions."""

import json
from types import SimpleNamespace

from pydantic import BaseModel


class School(BaseModel):
    """School class, offers a standardized single object to represent all educational institutions."""

    short_name: str  # Must be unique against all other schools.
    full_name: str
    description: str = ""
    alias: str | None = None
    region: str | None = None
    course_code_syntax: list[str]
    # course_code_syntax legend:
    # "@" = alphabetical character.
    # "#" = numerical character.
    # Course codes should always be alphanumeric.
    # Anything else = exact match.
    ratemyprof_api_id: str | None = None

    def is_valid_course_code(self, course_code: str) -> bool:
        """Check if a course_code is valid according to school syntax.

        Args:
            course_code: Course code string.

        Returns:
            True if valid, False if invalid.

        Examples:
            >>> s = School( \
                    short_name="YEET", \
                    full_name="Yeet University of Fairy Land", \
                    course_code_syntax=[ \
                        "@@@@####U", "@@@####U", "@@@@####G", "@@@####G" \
                    ], \
                )
            >>> s.is_valid_course_code("@RAD1234G")
            False
            >>> s.is_valid_course_code("GRAD1234G")
            True
            >>> s.is_valid_course_code("UNDG1234U")
            True
            >>> s.is_valid_course_code("m a TH 1 234 U")
            True
            >>> s.is_valid_course_code("qwert1234U")
            False
            >>> s.is_valid_course_code("qwer1234U")
            True
            >>> s.is_valid_course_code("qwe1234U")
            True
            >>> s.is_valid_course_code("qw1234U")
            False
            >>> s.is_valid_course_code("qwer123U")
            False
            >>> s.is_valid_course_code("qwer12345U")
            False
        """
        course_code = course_code.replace(" ", "").upper()
        if not course_code.isalnum():  # White spaces must be removed first.
            return False
        if not self.course_code_syntax:  # At least 1 syntax must be specified.
            return False
        attempting_syntax = self.course_code_syntax.copy()  # Exact character in syntax.
        for i, char in enumerate(course_code):  # Translate course code to syntax.
            if char.isalpha():
                char_translation = "@"
            else:  # char.isdigit():
                char_translation = "#"
            for syntax_str in attempting_syntax.copy():  # Use a copy to loop.
                # Copy is required since we're removing from the looping list.
                if syntax_str[i] != char and syntax_str[i] != char_translation:
                    attempting_syntax.remove(syntax_str)
            if not attempting_syntax:  # Out of possible syntax matches.
                return False
        return True

    def to_json(self) -> str:
        """Converts a School object to json str.

        Returns:
            json string of the School object.
        """

        def default(obj):
            return obj.__dict__

        return json.dumps(self, default=default, indent=4)

    @staticmethod
    def from_json(json_str: str):  # -> School:
        """Converts json str to a School object.

        Returns:
            json string of the School object.
        """
        simple = json.loads(json_str, object_hook=lambda d: SimpleNamespace(**d))

        return School(
            short_name=simple.short_name,
            full_name=simple.full_name,
            description=simple.description,
            alias=simple.alias,
            region=simple.region,
            course_code_syntax=simple.course_code_syntax,
            ratemyprof_api_id=simple.ratemyprof_api_id,
        )


def decode_school_from_json(json_file_path: str) -> School:
    """Acts as a decoder from a json config file to a School object.

    Potential FileNotFoundError raises!

    Args:
        json_file_path: Filepath of the json school file.

    Returns:
        A School object with the dumped/decoded information from the given
        filepath.
    """
    with open(json_file_path) as json_config_file:
        json_str = json_config_file.read()
    return School.from_json(json_str)
