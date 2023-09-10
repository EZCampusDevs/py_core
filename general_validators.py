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
