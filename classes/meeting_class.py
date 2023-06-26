"""Meeting class module.

The Meeting class is also the superclass of ExtendedMeeting.
"""

import json
from datetime import date, time, datetime, timedelta

from dateutil.rrule import (
    rrule,
    DAILY,
    WEEKLY,
    MONTHLY,
    YEARLY,
    MO,
    TU,
    WE,
    TH,
    FR,
    SA,
    SU,
)
from pydantic import BaseModel, root_validator, validator

from .. import constants
from .. import general

DAYS = {0: "MO", 1: "TU", 2: "WE", 3: "TH", 4: "FR", 5: "SA", 6: "SU"}


class Meeting(BaseModel):
    """Meeting class defines an instance of when a course meeting occurs."""

    time_start: time = time.min  # Meeting start time.
    time_end: time = time.max  # Meeting end time.
    # In the event times are not specified, assume corresponding min/max.
    date_start: date  # Meeting start date window.
    date_end: date  # Meeting end date window.
    occurrence_unit: None | str = None
    occurrence_interval: None | int = None
    # If occurrence_unit is None, occurrence_interval must be None.
    occurrence_limit: date | int | None = None
    # If occurrence_unit is None, occurrence_limit must be None.
    days_of_week: int = None  # Weekdays as 1 int value.
    # NOTE: Functionally speaking, days_of_week really only affects Meetings with the occurrence
    # unit of weeks. This is corrected to None by a root_validator if days_of_week is specified,
    # but not needed.
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
        if v not in constants.OU_ALLOWED:
            raise ValueError(
                f"occurrence_unit={v} is not allowed. Allowed units: {constants.OU_ALLOWED}"
            )
        return v

    @root_validator()
    def __override_course_occurrence_unit_correction(cls, values):
        """WARNING: THIS MUST RUN BEFORE THE CONFLICTING VALIDATORS."""
        # TODO: This is an override validator for course data. Ideally this should be done at the
        #  data/scraper level, but this works too.
        occurrence_unit = values.get("occurrence_unit")
        date_start = values.get("date_start")
        date_end = values.get("date_end")
        days_of_week = values.get("days_of_week")

        if (
            occurrence_unit is None
            and (date_end - date_start) >= timedelta(days=7)
            and isinstance(days_of_week, int)
            and days_of_week != 0
        ):
            values["occurrence_unit"] = constants.OU_WEEKS
            values["occurrence_interval"] = 1
            values["occurrence_limit"] = date_end
            new_date = min(
                [
                    forward_weekday_target(n, date_start)
                    for n in general.decode_weekday_ints(days_of_week)
                ]
            )
            values["date_start"] = new_date
            values["date_end"] = new_date
        return values

    @root_validator()
    def verify_occurrence_interval(cls, values):
        occurrence_unit = values.get("occurrence_unit")
        occurrence_interval = values.get("occurrence_interval")
        if occurrence_unit is not None and occurrence_interval < 1:
            raise ValueError(
                f"occurrence_unit={occurrence_unit}, expected occurrence_interval >= 1"
            )
        elif occurrence_unit is None and occurrence_interval is not None:
            raise ValueError(f"occurrence_unit={None}, expected occurrence_interval={None}")
        return values

    @root_validator()
    def verify_occurrence_limit(cls, values):
        occurrence_unit = values.get("occurrence_unit")
        occurrence_limit = values.get("occurrence_limit")
        if occurrence_unit is not None and occurrence_limit is None:
            raise ValueError(
                f"occurrence_unit={occurrence_unit}, expected occurrence_interval != {None}"
            )
        elif occurrence_unit is None and occurrence_limit is not None:
            raise ValueError(f"occurrence_unit={None}, expected occurrence_interval = {None}")
        return values

    @root_validator()
    def verify_days_of_week(cls, values):
        occurrence_unit = values.get("occurrence_unit")
        days_of_week = values.get("days_of_week")
        if occurrence_unit == constants.OU_WEEKS or occurrence_unit == constants.OU_MONTHS_WD:
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
            values["days_of_week"] = None
            # Alternative (error raising validation):
            # raise ValueError(f"occurrence_unit={occurrence_unit}, expected days_of_week={None}, got {days_of_week}")
        return values

    def decode_days_of_week(self) -> dict[str, bool]:
        return general.decode_days_of_week(self.days_of_week)

    def decode_weekday_ints(self) -> list[int]:
        return general.decode_weekday_ints(self.days_of_week)

    def get_rrule(self) -> rrule | None:
        if self.occurrence_unit == constants.OU_DAYS:
            return rrule(
                DAILY,
                dtstart=datetime.combine(self.date_start, self.time_start),
                until=datetime.combine(self.date_end, self.time_end),
                interval=self.occurrence_interval,
            )
        elif self.occurrence_unit == constants.OU_WEEKS:
            by_weekday = [MO, TU, WE, TH, FR, SA, SU]
            return rrule(
                WEEKLY,
                dtstart=datetime.combine(self.date_start, self.time_start),
                until=datetime.combine(self.date_end, self.time_end),
                interval=self.occurrence_interval,
                byweekday=[by_weekday[w_i] for w_i in self.decode_weekday_ints()],
            )
        elif self.occurrence_unit == constants.OU_MONTHS_WD:
            ordinal = (self.date_start.day - 1) // 7 + 1
            # Determine with nth date_start.weekday() that date_start is.
            by_weekday = [
                MO(ordinal),
                TU(ordinal),
                WE(ordinal),
                TH(ordinal),
                FR(ordinal),
                SA(ordinal),
                SU(ordinal),
            ]
            return rrule(
                MONTHLY,
                dtstart=datetime.combine(self.date_start, self.time_start),
                until=datetime.combine(self.date_end, self.time_end),
                interval=self.occurrence_interval,
                byweekday=by_weekday[self.date_start.weekday()],
            )
        elif self.occurrence_unit == constants.OU_MONTHS_N:
            return rrule(
                MONTHLY,
                dtstart=datetime.combine(self.date_start, self.time_start),
                until=datetime.combine(self.date_end, self.time_end),
                interval=self.occurrence_interval,
            )
        elif self.occurrence_unit == constants.OU_YEARS:
            return rrule(
                YEARLY,
                dtstart=datetime.combine(self.date_start, self.time_start),
                until=datetime.combine(self.date_end, self.time_end),
                interval=self.occurrence_interval,
            )
        else:  # self.occurrence_unit is None:
            return None

    def get_ics_rrule_str(self) -> str:
        def get_limit():
            if isinstance(self.occurrence_limit, int):
                return f"COUNT={self.occurrence_limit}"
            elif isinstance(self.occurrence_limit, date):
                dt_ol = datetime.combine(self.occurrence_limit, time.max).strftime("%Y%m%dT%H%M%S")
                return f"UNTIL={dt_ol}"
            else:
                raise TypeError(f"ex_mt.occurrence_limit must be type {date} or {int}")

        result = (
            f"DTSTART;TZID=America/Toronto:"
            f"{datetime.combine(self.date_start, self.time_start).strftime('%Y%m%dT%H%M%S')}\n"
            f"DTEND;TZID=America/Toronto:"
            f"{datetime.combine(self.date_end, self.time_end).strftime('%Y%m%dT%H%M%S')}\n"
        )

        if self.occurrence_unit == constants.OU_DAYS:
            result += f"RRULE:FREQ=DAILY;{get_limit()};INTERVAL={self.occurrence_interval}"
        elif self.occurrence_unit == constants.OU_WEEKS:
            result += (
                f"RRULE:FREQ=WEEKLY;{get_limit()}"
                f";BYDAY={','.join([DAYS[n] for n in self.decode_weekday_ints()])}"
                f";INTERVAL={self.occurrence_interval}"
            )
        elif self.occurrence_unit == constants.OU_MONTHS_WD:
            result += (
                f"RRULE:FREQ=MONTHLY;{get_limit()};INTERVAL={self.occurrence_interval}"
                f";BYDAY={(self.date_start.day - 1) // 7 + 1}{DAYS[self.date_start.weekday()]}"
            )
        elif self.occurrence_unit == constants.OU_MONTHS_N:
            result += (
                f"RRULE:FREQ=MONTHLY;{get_limit()};INTERVAL={self.occurrence_interval}"
                f";BYMONTHDAY={self.date_start.day}"
            )
        elif self.occurrence_unit == constants.OU_YEARS:
            result += f"RRULE:FREQ=YEARLY;{get_limit()};INTERVAL={self.occurrence_interval}"

        return result

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

    def get_raw_str(self):
        return (
            f"time_start={self.time_start}\n"
            f"time_end={self.time_end}\n"
            f"date_start={self.date_start}\n"
            f"date_end={self.date_end}\n"
            f"occurrence_unit={self.occurrence_unit}\n"
            f"occurrence_interval={self.occurrence_interval}\n"
            f"occurrence_limit={self.occurrence_limit}\n"
            f"days_of_week={self.days_of_week} -> ({self.decode_days_of_week()})\n"
            f"location={self.location}"
        )

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
        dt_obj = datetime.combine(date.min, dt_obj)
        # Convert datetime.time() to datetime.datetime().
        return (
            dt_obj.replace(hour=dt_obj.hour, minute=0, second=0, microsecond=0)
            + timedelta(hours=dt_obj.minute // 30)
        ).time()
    elif isinstance(dt_obj, datetime):
        return dt_obj.replace(hour=dt_obj.hour, minute=0, second=0, microsecond=0) + timedelta(
            hours=dt_obj.minute // 30
        )
    else:
        raise TypeError("Expected datetime.time() or datetime.datetime().")


def to_single_occurrences(mt: Meeting) -> list[Meeting]:
    """Breaks reoccurring meeting into individual non-reoccurring (single occurrence) Meetings."""
    if mt.occurrence_unit is None:
        return [mt]
    start_dates = mt.all_start_dates()
    return [
        Meeting(
            time_start=mt.time_start,
            time_end=mt.time_end,
            date_start=d,
            date_end=(d + timedelta(days=(mt.date_end - mt.date_start).days)),
            occurrence_unit=None,
            occurrence_interval=None,
            occurrence_limit=None,
            days_of_week=None,
            location=mt.location,
        )
        for d in start_dates
    ]


def merged_meeting_occurrences(mt_list: list[Meeting]) -> list[Meeting]:
    """Merge meetings via occurrences."""
    if not mt_list:
        return []

    weekly_mts = [mt for mt in mt_list if mt.occurrence_unit == constants.OU_WEEKS]
    non_weekly_mts = [mt for mt in mt_list if mt.occurrence_unit != constants.OU_WEEKS]

    merging = []
    for _ in weekly_mts:
        # while True + break would work here, but I don't trust myself, so I'm using a for.
        if len(weekly_mts) == 1:
            break
        count_save = len(weekly_mts)
        weekly_mts.sort(
            key=lambda mt: (
                mt.occurrence_unit,
                mt.time_start,
                mt.time_end,
                mt.occurrence_interval,
                mt.occurrence_limit,
                mt.location,
            )
        )
        for i in range(1, len(weekly_mts), 1):
            merging += merge_weekly_occurrences(mt_1=weekly_mts[i - 1], mt_2=weekly_mts[i])
        if len(merging) == count_save:  # Loop until merges are no longer possible.
            break
        weekly_mts = merging.copy()
    return non_weekly_mts + weekly_mts


def merge_weekly_occurrences(mt_1: Meeting, mt_2: Meeting) -> list[Meeting]:
    if mt_1.occurrence_unit == mt_2.occurrence_unit == constants.OU_WEEKS and (
        mt_1.time_start == mt_2.time_start
        and mt_1.time_end == mt_2.time_end
        and mt_1.occurrence_interval == mt_2.occurrence_interval
        and mt_1.occurrence_limit == mt_2.occurrence_limit
        and mt_1.location == mt_2.location
    ):
        weekday_ints = list(set(mt_1.decode_weekday_ints() + mt_2.decode_weekday_ints()))
        return [
            Meeting(
                time_start=mt_1.time_start,
                time_end=mt_1.time_end,
                date_start=min([mt_1.date_start, mt_2.date_start]),
                date_end=min([mt_1.date_end, mt_2.date_end]),
                occurrence_unit=mt_1.occurrence_unit,
                occurrence_interval=mt_1.occurrence_interval,
                occurrence_limit=mt_1.occurrence_limit,
                days_of_week=general.encode_weekday_ints(weekday_ints),
                location=mt_1.location,
            )
        ]
    return [mt_1, mt_2]


def meetings_conflict(
    mt_list: list[Meeting], detailed: bool = False
) -> bool | tuple[bool, None | datetime]:
    """Determines if a list of Meeting objects (schedule) is has time conflicts.

    Args:
        mt_list: List of Meeting objects.
        detailed: If True, return will be a tuple which includes the conflicting datetime.

    Notes:
        The datetime returned in the tuple if the parameter detailed is True is propagated from
        meeting_conflict(). Due to the sorting and the datetime standard weekday values used in
        this function, the datetime returned will be for the first conflict found.
        (Monday -> Sunday, early -> later time).

    Returns:
        True if a list of Meetings has a time conflict(s), False if no time conflict(s) exist.
    """
    if len(mt_list) <= 1:
        return (False, None) if detailed else False

    no_occurrence_mts = []

    for mt in mt_list:
        if mt.occurrence_unit is None:
            no_occurrence_mts.append(mt)
        else:
            no_occurrence_mts += to_single_occurrences(mt)
            # Convert to non-reoccurring Meetings to run 1-1 comparison.

    if len(no_occurrence_mts) >= 3:  # More than 3 meetings to compare.
        no_occurrence_mts.sort(key=lambda m: (m.date_start, m.time_start, m.time_end))
        # 1. m.date_start. <low/early to high/later>.
        # 2. m.time_start. <low/early to high/later>.
        # 3. m.time_end. <low/early to high/later>.
        # Sorting ensures only the minimum comparisons are made.
        for i in range(1, len(no_occurrence_mts)):
            conflict_detailed = meeting_conflict(
                no_occurrence_mts[i - 1], no_occurrence_mts[i], detailed=True
            )
            if conflict_detailed[0]:  # Validate pairs: (1, 2, 3) -> (1 vs 2, 2 vs 3).
                return (True, conflict_detailed[1]) if detailed else True
    elif len(no_occurrence_mts) == 2:  # Exactly 2 meetings to compare.
        conflict_detailed = meeting_conflict(
            no_occurrence_mts[0], no_occurrence_mts[1], detailed=True
        )
        if conflict_detailed[0]:  # Validate pair.
            return (True, conflict_detailed[1]) if detailed else True
    return (False, None) if detailed else False


def meeting_conflict(
    mt_1: Meeting, mt_2: Meeting, detailed: bool = False
) -> tuple[bool, datetime] | bool:
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

    if mt_1.occurrence_unit is not None or mt_2.occurrence_unit is not None:
        raise ValueError(
            f"Meeting must be of occurrence_unit={None} to do 1-1 meeting conflict comparisons."
        )

    # 1 to 1 comparison.
    dc = date_conflict()
    tc = time_conflict()
    if dc[0] and tc[0]:
        return (True, datetime.combine(dc[1], tc[1])) if detailed else True
    else:
        return (False, None) if detailed else False


def forward_weekday_target(target_weekday_int: int, base_date: date) -> date:
    """Get the first date that matches the target weekday in that falls on or after the base date.

    Args:
        target_weekday_int: Target weekday we want on the date.
            Follows datetime.datetime.weekday() index convention: (0 = Monday, 6 = Sunday).
        base_date: Initial date to start on.

    Returns:
        New date with the correct target weekday.

    Examples:
        >>> forward_weekday_target(target_weekday_int=0, base_date=date(2022, 4, 1))
        datetime.date(2022, 4, 4)
        >>> forward_weekday_target(target_weekday_int=4, base_date=date(2022, 4, 1))
        datetime.date(2022, 4, 1)
        >>> forward_weekday_target(target_weekday_int=5, base_date=date(2022, 4, 1))
        datetime.date(2022, 4, 2)
    """
    target_delta_int = target_weekday_int - base_date.weekday()  # Calculate the shift required.
    target_delta_int += 7 if target_delta_int < 0 else 0
    # If your  target is Monday and the start_time = Wednesday, target_delta_int shifts to the next
    # future Monday (Not going backwards to a past Monday).
    return base_date + timedelta(days=target_delta_int)  # Shifted date.


def backward_target_weekday(target_weekday_int: int, base_date: date) -> date:
    """Get the last date that matches the target weekday in that falls on or before the base date.

    Args:
        target_weekday_int: Target weekday we want on the date.
            Follows datetime.datetime.weekday() index convention: (0 = Monday, 6 = Sunday).
        base_date: Initial date to start on.

    Returns:
        New date with the correct target weekday.

    Examples:
        >>> backward_target_weekday(target_weekday_int=0, base_date=date(2022, 4, 30))
        datetime.date(2022, 4, 25)
        >>> backward_target_weekday(target_weekday_int=4, base_date=date(2022, 4, 30))
        datetime.date(2022, 4, 29)
        >>> backward_target_weekday(target_weekday_int=5, base_date=date(2022, 4, 30))
        datetime.date(2022, 4, 30)
    """
    target_delta_int = target_weekday_int - base_date.weekday()  # Calculate the shift required.
    target_delta_int -= 7 if target_delta_int > 0 else 0
    # If your target is Monday and the start_time = Wednesday, target_delta_int shifts to the
    # previous past Monday (Not going forward to the future Monday).
    return base_date + timedelta(days=target_delta_int)  # Shifted date.
