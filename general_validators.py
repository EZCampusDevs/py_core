"""
General validator code.
"""

import re


def is_valid_hexadecimal_colour(str_hexadecimal: str) -> bool:
    """Validate a string hexadecimal code.

    Args:
        str_hexadecimal:

    Returns:
        True for valid, False for invalid.

    Examples:
        >>> is_valid_hexadecimal_colour("#FFFFFF")
        True
        >>> is_valid_hexadecimal_colour("FFFFFF")
        False
        >>> is_valid_hexadecimal_colour("FFFFFFFFFFFFF")
        False
        >>> is_valid_hexadecimal_colour("ZZZZZZ")
        False
    """
    if isinstance(str_hexadecimal, str):
        if re.search(r"^#(?:[0-9a-fA-F]{3}){1,2}$", str_hexadecimal.replace(" ", "")):
            return True
    return False
