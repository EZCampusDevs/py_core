"""Meeting class module.

The Meeting class is also the superclass of ExtendedMeeting.
"""

import json
from datetime import date, time, datetime, timedelta
from types import SimpleNamespace

from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY, YEARLY, MO, TU, WE, TH, FR, SA, SU
from pydantic import BaseModel, root_validator, validator

from .. import general


class Meeting(BaseModel):
    """Meeting class defines an instance of when a course meeting occurs."""
    time_start: time = time.min  # Meeting start time.
    time_end: time = time.max  # Meeting end time, In the event times are not specified, assume all day Meeting.
    date_start: date  # Meeting start date window.
    date_end: date  # Meeting end date window.
    occurrence_unit: None | str
    occurrence_interval: None | int  # If occurrence_unit is None, occurrence_interval must be None.
    days_of_week: None | int  # Weekdays as 1 int value, days_of_week is not None only when occurrence_unit is "weeks".
    location: str = ""

    @root_validator()
    def verify_valid_times(cls, values):
        time_start = values.get("time_start")
        time_end = values.get("time_end")
        if not (time_start < time_end):
            raise ValueError(f"Expected time_start={time_start} < time_end={time_end}")
        return values

    @root_validator()
    def verify_valid_dates(cls, values):
        date_start = values.get("date_start")
        date_end = values.get("date_end")
        if not (date_start <= date_end):
            raise ValueError(f"Expected date_start={date_start} <= date_end={date_end}")
        return values

    @validator("occurrence_unit")
    def verify_occurrence_unit(cls, v):
        ALLOWED_UNITS = [None, "days(n)", "weeks(weekday)", "months(nth_weekday)", "months(nth)", "years(nth)"]
        if v not in ALLOWED_UNITS:
            raise ValueError(f"occurrence_unit={v} is not allowed. Must be one of the following: {ALLOWED_UNITS}")
        return v

    @root_validator()
    def verify_occurrence_interval(cls, values):
        occurrence_unit = values.get("occurrence_unit")
        occurrence_interval = values.get("occurrence_interval")
        if occurrence_unit is not None and occurrence_interval < 1:
            raise ValueError(f"occurrence_unit={occurrence_unit}, expected occurrence_interval >= 1")
        elif occurrence_unit is None and occurrence_interval is not None:
            raise ValueError(f"occurrence_unit={None}, expected occurrence_interval = {None}")
        return values

    @root_validator()
    def verify_days_of_week(cls, values):
        occurrence_unit = values.get("occurrence_unit")
        days_of_week = values.get("days_of_week")
        if occurrence_unit == "weeks(weekday)":
            if days_of_week is None:
                raise ValueError(f"occurrence_unit={occurrence_unit}, days_of_week cannot be {None}")
            try:
                weekday_ints = general.decode_weekday_ints(days_of_week)
                if len(weekday_ints) != len(set(weekday_ints)):
                    raise ValueError(f"Caught duplicates in {weekday_ints}")
                unexpected_ints = [i for i in weekday_ints if (i < 0 or i > 6)]
                if unexpected_ints:
                    raise ValueError(f"Caught unexpected values in {weekday_ints}")
            except:
                raise ValueError(f"Incorrect usage of days_of_week")
        elif days_of_week is not None:
            raise ValueError(
                f"occurrence_unit={occurrence_unit}, expected days_of_week={None}, got days_of_week={days_of_week}")
        return values

    def decode_days_of_week(self) -> dict[str, bool]:
        return general.decode_days_of_week(self.days_of_week)

    def decode_weekday_ints(self) -> list[int]:
        return [i for i, val in enumerate(self.decode_days_of_week().values()) if val]

    def get_rrule(self) -> rrule | None:
        if self.occurrence_unit == "days(n)":
            return rrule(DAILY, dtstart=self.date_start, until=self.date_end, interval=self.occurrence_interval)
        elif self.occurrence_unit == "weeks(weekday)":
            return rrule(WEEKLY, dtstart=self.date_start, until=self.date_end, interval=self.occurrence_interval)
        elif self.occurrence_unit == "months(nth_weekday)":
            ordinal = (self.date_start.day - 1) // 7 + 1  # Determine with nth date_start.weekday() that date_start is.
            by_weekday = [MO(ordinal), TU(ordinal), WE(ordinal), TH(ordinal), FR(ordinal), SA(ordinal), SU(ordinal)]
            return rrule(MONTHLY, dtstart=self.date_start, until=self.date_end, interval=self.occurrence_interval,
                         byweekday=by_weekday[self.date_start.weekday()])
        elif self.occurrence_unit == "months(nth)":
            return rrule(MONTHLY, dtstart=self.date_start, until=self.date_end, interval=self.occurrence_interval)
        elif self.occurrence_unit == "years(nth)":
            return rrule(YEARLY, dtstart=self.date_start, until=self.date_end, interval=self.occurrence_interval)
        else:  # self.occurrence_unit is None:
            return None

    def all_start_dates(self) -> list[date]:
        mt_rrule = self.get_rrule()
        if isinstance(mt_rrule, rrule):
            return [dt.date() for dt in list(mt_rrule)]
        else:
            return [self.date_start]

    def num_of_occurrences(self) -> int:
        return len(self.all_start_dates())

    def to_json(self) -> str:
        """Converts a Meeting object to json str.

        Returns:
            json string of the Meeting object.
        """

        def default(obj):
            if isinstance(obj, date):
                return obj.isoformat()
            if isinstance(obj, time):
                return obj.isoformat()
            if isinstance(obj, int):
                return obj
            if isinstance(obj, str):
                return obj
            else:
                return obj.__dict__

        return json.dumps(self, default=default)

    @staticmethod
    def from_json(json_str: str):  # -> Meeting:
        """Converts a json str to Meeting object.

        Args:
            json_str: json string of the Course object to decode from.

        Returns:
            Course from the decoded object.
        """
        simple = json.loads(json_str, object_hook=lambda d: SimpleNamespace(**d))
        return Meeting(time_start=simple.time_start, time_end=simple.time_end, days_of_week=simple.days_of_week,
                       date_start=simple.date_start, date_end=simple.date_end,
                       occurrence_timedelta_days=simple.occurrence_timedelta_days, location=simple.location)

    def get_raw_str(self):
        return (f"time_start={self.time_start}\n"
                f"time_end={self.time_end}\n"
                f"date_start={self.date_start}\n"
                f"date_end={self.date_end}\n"
                f"occurrence_unit={self.occurrence_unit}\n"
                f"occurrence_interval={self.occurrence_interval}\n"
                f"days_of_week={self.days_of_week} -> ({self.decode_days_of_week()})\n"
                f"location={self.location}")

    def __str__(self):
        return self.get_raw_str()


def round_to_hour(dt_obj: time | datetime) -> time | datetime:
    """Rounds to the nearest hour by adding a timedelta hour if time.minute >= 30.

    Args:
        dt_obj: datetime.time() or datetime.datetime().

    Returns:
        Rounded time.

    Examples:
        >>> round_to_hour(datetime(2022, 9, 1, 10, 30))
        datetime.datetime(2022, 9, 1, 11, 0)
        >>> round_to_hour(time(10, 30))
        datetime.time(11, 0)
        >>> round_to_hour(time(10, 29))
        datetime.time(10, 0)
        >>> round_to_hour(time(0, 29))
        datetime.time(0, 0)
        >>> round_to_hour(time(23, 30))
        datetime.time(0, 0)
    """
    if isinstance(dt_obj, time):
        dt_obj = datetime.combine(date.min, dt_obj)  # Convert datetime.time() to datetime.datetime().
        return (dt_obj.replace(hour=dt_obj.hour, minute=0, second=0, microsecond=0)
                + timedelta(hours=dt_obj.minute // 30)).time()
    elif isinstance(dt_obj, datetime):
        return (dt_obj.replace(hour=dt_obj.hour, minute=0, second=0, microsecond=0)
                + timedelta(hours=dt_obj.minute // 30))
    else:
        raise TypeError("Expected datetime.time() or datetime.datetime().")


def to_single_occurrences(mt: Meeting) -> list[Meeting]:
    """Breaks down reoccurring meeting into individual non-reoccurring (single occurrence) Meetings."""
    if mt.occurrence_unit is None:
        return [mt]
    start_dates = mt.all_start_dates()
    return [Meeting(time_start=mt.time_start, time_end=mt.time_end, date_start=d,
                    date_end=(d + timedelta(days=(mt.date_end - mt.date_start).days)), occurrence_unit=None,
                    occurrence_interval=None, days_of_week=None, location=mt.location) for d in start_dates]


def meetings_conflict(mt_list: list[Meeting], detailed: bool = False) -> bool | tuple[bool, None | datetime]:
    """Determines if a list of Meeting objects (schedule) is has time conflicts.

    Args:
        mt_list: List of Meeting objects.
        detailed: If True, return will be a tuple which includes the conflicting datetime.

    Notes:
        The datetime returned in the tuple if the parameter detailed is True is propgated from meeting_conflict(). Due
        to the sorting and the datetime standard weekday values used in this function, the datetime returned will be
        for the first conflict found (Monday -> Sunday, early -> later time).

    Returns:
        False if a list of Meetings has a time conflict(s), True if no time conflict(s) exist.
    """
    if len(mt_list) <= 1:
        return (False, None) if detailed else False

    # Initialize meeting times list.
    week = [[], [], [], [], [], [], []]  # Each index represents a weekday.
    # [Monday, Tuesday, ..., Sunday] <- Using weekday indexes.

    for meeting in mt_list:
        for i, val in enumerate(meeting.decode_days_of_week().values()):
            if val:
                week[i].append(meeting)

    for day in week:
        if len(day) >= 3:  # More than 3 meetings to compare.
            day.sort(key=lambda mt: (
                mt.get_actual_date_start(),  # 1. mt.get_actual_date_start(). <low/early to high/later>.
                mt.time_start,  # 2. mt.time_start. <low/early to high/later>.
                mt.time_end  # 3. mt.time_end. <low/early to high/later>.
            ))  # Sorting ensures only the core required comparisons are made, reducing unneeded computation.
            for i in range(1, len(day)):
                conflict_detailed = meeting_conflict(day[i - 1], day[i], detailed=True)
                # Validate pairs: (1, 2, 3) -> (1 vs 2, 2 vs 3).
                if conflict_detailed[0]:
                    return (True, conflict_detailed[1]) if detailed else True
        elif len(day) == 2:  # Exactly 2 meetings to compare.
            conflict_detailed = meeting_conflict(day[0], day[1], detailed=True)
            # Validate pair.
            if conflict_detailed[0]:
                return (True, conflict_detailed[1]) if detailed else True
    return (False, None) if detailed else False


def meeting_conflict(mt_1: Meeting, mt_2: Meeting, detailed: bool = False) -> tuple[bool, datetime] | bool:
    """Determine and identify 2 Meeting objects conflicting on date and/or time.

    Args:
        mt_1: Meeting object 1.
        mt_2: Meeting object 2.
        detailed: If True, return will be a tuple which includes the first conflicting datetime.

    Returns:
        Boolean for if for conflict exists, conflicting datetime, None if no datetime.
    """

    def time_conflict() -> tuple[bool, time | None]:
        if mt_1.time_start <= mt_2.time_start < mt_1.time_end:
            return True, mt_2.time_start
        if mt_2.time_start <= mt_1.time_start < mt_2.time_end:
            return True, mt_1.time_start
        if mt_1.time_start < mt_2.time_end <= mt_1.time_end:
            return True, mt_1.time_start
        if mt_2.time_start < mt_1.time_end <= mt_2.time_end:
            return True, mt_2.time_start
        return False, None

    def date_conflict() -> tuple[bool, date | None]:
        if mt_1.date_start <= mt_2.date_start < mt_1.date_end:
            return True, mt_2.date_start
        if mt_2.date_start <= mt_1.date_start < mt_2.date_end:
            return True, mt_1.date_start
        if mt_1.date_start < mt_2.date_end <= mt_1.date_end:
            return True, mt_1.date_start
        if mt_2.date_start < mt_1.date_end <= mt_2.date_end:
            return True, mt_2.date_start
        return False, None

    if mt_1.occurrence_unit is None and mt_2.verify_occurrence_unit is None:  # 1 to 1 comparison.
        dc = date_conflict()
        tc = time_conflict()
        if dc[0] and tc[0]:
            return (True, datetime.combine(dc[1], tc[1])) if detailed else True
        else:
            return (False, None) if detailed else False
    else:  # Convert everything to non-reoccurring Meetings and run a comparison.
        single_occurrence = []
        if mt_1.occurrence_unit is None:
            single_occurrence += to_single_occurrences(mt_1)
        else:
            single_occurrence.append(mt_1)
        if mt_2.occurrence_unit is None:
            single_occurrence += to_single_occurrences(mt_2)
        else:
            single_occurrence.append(mt_2)
        return meetings_conflict(mt_list=single_occurrence, detailed=detailed)
