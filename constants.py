"""
Constants related to program computation.
"""

BRAND = "fastapi_backend"

# Days of the week representation.
#  2 has a value of 0010 in binary, so it would be Tuesday.
#  3 has a value of 0011 in binary, so it would be Monday, Tuesday.
MONDAY = 0b000_0001
TUESDAY = 0b000_0010
WEDNESDAY = 0b000_0100
THURSDAY = 0b000_1000
FRIDAY = 0b001_0000
SATURDAY = 0b010_0000
SUNDAY = 0b100_0000

# Meeting class occurrence units.
OU_DAYS = "DAILY"
OU_WEEKS = "WEEKLY"
OU_MONTHS_WD = "MONTHLY(nth_weekday)"
OU_MONTHS_N = "MONTHLY(nth_day)"
OU_YEARS = "YEARLY"
OU_ALLOWED = [None, OU_DAYS, OU_WEEKS, OU_MONTHS_WD, OU_MONTHS_N, OU_YEARS]

# Minimum and maximum character lengths. If a minimum is not specified it's because it can be None.
USERNAME_MIN_LEN = 4
USERNAME_MAX_LEN = 30
EMAIL_MIN_LEN = 8
EMAIL_MAX_LEN = 255
PASS_MIN_LEN = 8
PASS_MAX_LEN = 255
NAME_MIN_LEN = 2
NAME_MAX_LEN = 50
DESC_MAX_LEN = 150
PROGRAM_MAX_LEN = 255
YEAR_OF_STUDY_MIN = 0  # 0 = Unspecified.
YEAR_OF_STUDY_MAX = 8

CUMULATIVE_PROGRAM_MAP_KEY_WORD = "CUMULATIVE"
