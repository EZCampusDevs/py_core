"""Meeting class module.

The Meeting class defines each instance a course has a meeting:
    If that specific meeting repeats, the repeat delta is in an integer representing the day time delta, typically 7 or
    14 representing weekly and biweekly meetings.

The Meeting class is also the superclass of ExtendedMeeting.
"""

import json
from datetime import date, time, datetime, timedelta
from types import SimpleNamespace
from typing import Optional

# TEST CODE ############################################################################################################
# import matplotlib.pyplot as plt
# TEST CODE ############################################################################################################
from pydantic import BaseModel, root_validator

from .. import general


class Meeting(BaseModel):
    """Meeting class defines an instance of when a course meeting occurs.

    time_start: Meeting start time.
    time_end: Meeting end time.
    days_of_week: Days of the week as int value.
        Follows datetime.datetime.weekday() index convention (0 = Monday, 1 = Tuesday, ..., 6 = Sunday).
    date_start: Meeting start date window.
    date_end: Meeting end date window.
    repeat_timedelta_days: Represents a datetime.timedelta in days showing meeting repeat intervals, if a meeting does
        not value = 0.
    location: Location info.

    Notes:
        Repetition via repeat_timedelta_days is only allowed if the meeting is less than or equal to 1 day.
    """
    time_start: time = time.min
    time_end: time = time.max
    # In the event times are not specified, assume all day Meeting.
    days_of_week: int
    date_start: date
    date_end: date
    repeat_timedelta_days: int = 0
    location: Optional[str]

    @root_validator()
    def verify_valid_time(cls, values):
        time_start = values.get("time_start")
        time_end = values.get("time_end")
        if not (time_start < time_end):
            raise ValueError(f"Expected time_start={time_start} < time_end={time_end}")
        return values

    @root_validator()
    def verify_valid_date(cls, values):
        date_start = values.get("date_start")
        date_end = values.get("date_end")
        if not (date_start <= date_end):
            raise ValueError(f"Expected date_start={date_start} <= date_end={date_end}")
        return values

    @root_validator()
    def verify_allowed_repeat_timedelta_days(cls, values):
        # TODO(Daniel): This protects to repeat timedelta days that have not been extensively tested. Program designed
        #  for intervals of multiples of 7 days.
        repeat_timedelta_days = values.get("repeat_timedelta_days")
        allowed_repeat_timedelta_days = [0, 7, 14, 28, 56]  # No repeat, weekly, biweekly, monthly, bimonthly.
        if repeat_timedelta_days not in allowed_repeat_timedelta_days:
            raise ValueError(f"repeat_timedelta_days={repeat_timedelta_days} is not allowed. Must be one of the "
                             f"following: {allowed_repeat_timedelta_days}")
        return values

    @root_validator()
    def verify_valid_weekday_int(cls, values):
        # verify_valid_date() and verify_allowed_repeat_timedelta_days() root_validator()s must pass successfully first.
        date_start = values.get("date_start")
        date_end = values.get("date_end")
        weekday_int = values.get("weekday_int")
        repeat_timedelta_days = values.get("repeat_timedelta_days")
        if repeat_timedelta_days == 0 and date_start.weekday() != weekday_int:
            raise ValueError(f"weekday_int={weekday_int} is not valid given repeat_timedelta_days=0 and date_start="
                             f"{date_start}")
        else:
            shifted_date = forward_weekday_target(
                target_weekday_int=weekday_int, base_date=date_start)
            if not (date_start <= shifted_date <= date_end):
                raise ValueError(f"weekday_int={weekday_int} is not valid within the given date_start={date_start} and "
                                 f"date_end={date_end}")
        return values

    def decode_days_of_week(self) -> dict[str, bool]:
        return general.decode_days_of_week(self.days_of_week)

    def get_actual_date_start(self) -> date:
        """Get the actual date of the first matching weekday_int.

        Returns:
            First datetime.date of the actual date which the meeting starts.
        """
        return min([forward_weekday_target(i, self.date_start)
                    for i, val in enumerate(self.decode_days_of_week().values()) if val])

    def get_actual_date_end(self) -> date:
        """Get the actual date of the last matching weekday_int.

        Returns:
            Last datetime.date of the actual date which the meeting ends.
        """
        return max([backward_target_weekday(i, self.date_end)
                    for i, val in enumerate(self.decode_days_of_week().values()) if val])

    def num_actual_meetings(self) -> int:
        """Get the number of times a meeting actually occurs essentially is the sum of each reoccurrence.

        Returns:
            Number of times a class meets.

        Notes:
            Potential logic error due to bad data in of self.date_start and self.date_end. For example, courses are set
            to occur every week in a semester, but do not account for reading week which removes 1 occurrence. Thus, 1
            extra recurrence that does not actually exist is counted. To correct this behaviour courses would need to
            split meetings into 2 instances. One repeating each week till before reading week, then starting again
            after.
        """
        if self.repeat_timedelta_days > 0:  # Account for reoccurrence.
            return (self.get_actual_date_end() - self.get_actual_date_start()).days // self.repeat_timedelta_days + 1
        return 1  # Single day, no reoccurrence.

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
                       repeat_timedelta_days=simple.repeat_timedelta_days, location=simple.location)

    def get_raw_str(self):
        return (f"time_start={self.time_start}\n"
                f"time_end={self.time_end}\n"
                f"days_of_week={self.days_of_week} -> ({self.decode_days_of_week()})\n"
                f"date_start={self.date_start}\n"
                f"date_end={self.date_end}\n"
                f"repeat_timedelta_days={self.repeat_timedelta_days}\n"
                f"location={self.location}")

    def __str__(self):
        return self.get_raw_str()


def forward_weekday_target(target_weekday_int: int, base_date: date) -> date:
    """Get the first instance of a date that matches the target weekday in that falls on or after the base date.

    Args:
        target_weekday_int: Target weekday we want on the date.
            Follows datetime.datetime.weekday() index convention (0 = Monday, 1 = Tuesday, ..., 6 = Sunday).
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
    target_delta_int += 7 if target_delta_int < 0 else 0  # If your  target is Monday and the start_time = Wednesday,
    # target_delta_int shifts to the next future Monday (Not going backwards to a past Monday).
    return base_date + timedelta(days=target_delta_int)  # Shifted date.


def backward_target_weekday(target_weekday_int: int, base_date: date) -> date:
    """Get the last instance of a date that matches the target weekday in that falls on or before the base date.

    Args:
        target_weekday_int: Target weekday we want on the date.
            Follows datetime.datetime.weekday() index convention (0 = Monday, 1 = Tuesday, ..., 6 = Sunday).
        base_date: Initial date to start on.

    Returns:
        New date with the correct target weekday.

    Examples:
        >>> backward_target_weekday(target_weekday_int=0, \
        base_date=date(2022, 4, 30))
        datetime.date(2022, 4, 25)
        >>> backward_target_weekday(target_weekday_int=4, \
        base_date=date(2022, 4, 30))
        datetime.date(2022, 4, 29)
        >>> backward_target_weekday(target_weekday_int=5, \
        base_date=date(2022, 4, 30))
        datetime.date(2022, 4, 30)
    """
    target_delta_int = target_weekday_int - base_date.weekday()  # Calculate the shift required.
    target_delta_int -= 7 if target_delta_int > 0 else 0  # If your target is Monday and the start_time = Wednesday,
    # target_delta_int shifts to the previous past Monday (Not going forward to the future Monday).
    return base_date + timedelta(days=target_delta_int)  # Shifted date.


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


def meetings_are_time_valid(mt_list: list[Meeting], detailed: bool = False) -> bool | tuple[bool, None | datetime]:
    """Determines if a list of Meeting objects (schedule) is has time conflicts.

    Args:
        mt_list: List of Meeting objects.
        detailed: If True, return will be a tuple which includes the conflicting datetime.

    Notes:
        The datetime returned in the tuple if the parameter detailed is True is propgated from meeting_conflict(). Due
        to the sorting and the datetime standard weekday values used in this function, the datetime returned will be
        for the first conflict found (Monday -> Sunday, early -> later time).

    Returns:
        True if a list of Meetings has no time conflicts, False if time conflicts exist.

    Examples:
        >>> from datetime import time, date
        >>> meetings_are_time_valid( \
            [Meeting(time_start=time(8, 0), time_end=time(10, 0), date_start=date(2022, 8, 1), \
                     date_end=date(2022, 8, 1), weekday_int=0, repeat_timedelta_days=0), \
            Meeting(time_start=time(8, 30), time_end=time(9, 0), date_start=date(2022, 8, 1), \
                    date_end=date(2022, 8, 1), weekday_int=0, repeat_timedelta_days=0)] \
            )  # 2 0-repeating meetings.
        False
        >>> meetings_are_time_valid( \
            [Meeting(time_start=time(8, 0), time_end=time(10, 0), date_start=date(2022, 8, 1), \
                     date_end=date(2022, 8, 1), weekday_int=0, repeat_timedelta_days=0), \
            Meeting(time_start=time(8, 0), time_end=time(10, 0), date_start=date(2022, 8, 2), \
                    date_end=date(2022, 8, 2), weekday_int=1, repeat_timedelta_days=0)] \
            )  # 2 0-repeating meetings, no day match.
        True
        >>> meetings_are_time_valid( \
            [Meeting(time_start=time(8, 0), time_end=time(10, 0), date_start=date(2022, 8, 1), \
                     date_end=date(2022, 8, 1), weekday_int=0, repeat_timedelta_days=0), \
            Meeting(time_start=time(8, 0), time_end=time(10, 0), date_start=date(2022, 8, 2), \
                    date_end=date(2022, 8, 2), weekday_int=1, repeat_timedelta_days=0)], detailed=True \
            )  # 2 0-repeating meetings, no day match.
        (True, None)
        >>> meetings_are_time_valid( \
            [Meeting(time_start=time.min, time_end=time.max, date_start=date(2022, 8, 1), date_end=date(2022, 8, 15), \
                     weekday_int=0, repeat_timedelta_days=7), \
            Meeting(time_start=time(8, 0), time_end=time(10, 0), date_start=date(2022, 8, 15), \
                    date_end=date(2022, 8, 15), weekday_int=0, repeat_timedelta_days=0)], detailed=True \
            )  # 1 0-repeating and 1 repeating meeting.
        (False, datetime.datetime(2022, 8, 15, 0, 0))
        >>> meetings_are_time_valid( \
            [Meeting(time_start=time(8, 0), time_end=time(10, 0), date_start=date(2022, 8, 1), \
                     date_end=date(2022, 8, 15), weekday_int=0, repeat_timedelta_days=7), \
            Meeting(time_start=time(10, 1), time_end=time(12, 0), date_start=date(2022, 8, 15), \
                    date_end=date(2022, 8, 15), weekday_int=0, repeat_timedelta_days=0)], detailed=True \
            )  # 1 0-repeating and 1 repeating meeting.
        (True, None)
        >>> meetings_are_time_valid( \
            [Meeting(time_start=time.min, time_end=time.max, date_start=date(2022, 8, 1), date_end=date(2022, 8, 15), \
                     weekday_int=0, repeat_timedelta_days=7), \
            Meeting(time_start=time.min, time_end=time.max, date_start=date(2022, 8, 2), date_end=date(2022, 8, 16), \
                    weekday_int=1, repeat_timedelta_days=7)], detailed=True \
            )  # 2 repeating meetings, no day match.
        (True, None)
        >>> meetings_are_time_valid( \
            [Meeting(time_start=time(8, 0), time_end=time(10, 0), date_start=date(2022, 8, 1), \
                     date_end=date(2022, 8, 15), weekday_int=0, repeat_timedelta_days=7), \
            Meeting(time_start=time(11, 0), time_end=time(12, 0), date_start=date(2022, 8, 1), \
                    date_end=date(2022, 8, 15), weekday_int=0, repeat_timedelta_days=7)], detailed=True \
            )  # 2 repeating meetings, no time match.
        (True, None)
        >>> meetings_are_time_valid( \
            [Meeting(time_start=time(8, 0), time_end=time(10, 0), date_start=date(2022, 8, 1), \
                     date_end=date(2022, 8, 1), weekday_int=0, repeat_timedelta_days=0), \
            Meeting(time_start=time(8, 0), time_end=time(10, 0), date_start=date(2022, 8, 2), \
                    date_end=date(2022, 8, 2), weekday_int=1, repeat_timedelta_days=0)], detailed=True \
            )  # 2 0-repeating meetings, no day match.
        (True, None)
        >>> meetings_are_time_valid( \
            [Meeting(time_start=time(8, 0), time_end=time(10, 0), date_start=date(2022, 8, 1), \
                     date_end=date(2022, 8, 1), weekday_int=0, repeat_timedelta_days=0), \
            Meeting(time_start=time(8, 30), time_end=time(9, 0), date_start=date(2022, 8, 1), \
                    date_end=date(2022, 8, 1), weekday_int=0, repeat_timedelta_days=0)], detailed=True \
            )  # 2 0-repeating meetings.
        (False, datetime.datetime(2022, 8, 1, 8, 30))
        >>> meetings_are_time_valid( \
            [Meeting(time_start=time(9, 0), time_end=time(10, 0), date_start=date(2023, 5, 1), \
                     date_end=date(2023, 5, 1), weekday_int=0, repeat_timedelta_days=0), \
            Meeting(time_start=time(9, 10), time_end=time(11, 0), date_start=date(2023, 6, 26), \
                    date_end=date(2023, 8, 4), weekday_int=0, repeat_timedelta_days=7)], detailed=True \
            )  # 2 0-repeating meetings.
        (True, None)
    """
    if len(mt_list) <= 1:
        return (True, None) if detailed else True

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
                    return (False, conflict_detailed[1]) if detailed else False
        elif len(day) == 2:  # Exactly 2 meetings to compare.
            conflict_detailed = meeting_conflict(day[0], day[1], detailed=True)
            # Validate pair.
            if conflict_detailed[0]:
                return (False, conflict_detailed[1]) if detailed else False
    return (True, None) if detailed else True


def meeting_conflict(mt_1: Meeting, mt_2: Meeting, detailed: bool = False) -> bool | tuple[bool, None | datetime]:
    """Determine and identify 2 Meeting objects conflicting on date and/or time.

    Args:
        mt_1: Meeting object 1.
        mt_2: Meeting object 2.
        detailed: If True, return will be a tuple which includes the conflicting datetime.

    Returns:
        Boolean for if for conflict exists, conflicting datetime, None if no datetime.

    Examples:
        >>> from datetime import time, date
        >>> meeting_conflict( \
            Meeting(time_start=time(8, 0), time_end=time(10, 0), date_start=date(2022, 8, 1), \
                    date_end=date(2022, 8, 1), weekday_int=0, repeat_timedelta_days=0), \
            Meeting(time_start=time(8, 30), time_end=time(9, 0), date_start=date(2022, 8, 1), \
                    date_end=date(2022, 8, 1), weekday_int=0, repeat_timedelta_days=0) \
            )  # 2 0-repeating meetings.
        True
        >>> meeting_conflict( \
            Meeting(time_start=time(8, 0), time_end=time(10, 0), date_start=date(2022, 8, 1), \
                    date_end=date(2022, 8, 1), weekday_int=0, repeat_timedelta_days=0), \
            Meeting(time_start=time(8, 0), time_end=time(10, 0), date_start=date(2022, 8, 2), \
                    date_end=date(2022, 8, 2), weekday_int=1, repeat_timedelta_days=0) \
            )  # 2 0-repeating meetings, no day match.
        False
        >>> meeting_conflict( \
            Meeting(time_start=time(8, 0), time_end=time(10, 0), date_start=date(2022, 8, 1), \
                    date_end=date(2022, 8, 1), weekday_int=0, repeat_timedelta_days=0), \
            Meeting(time_start=time(8, 0), time_end=time(10, 0), date_start=date(2022, 8, 2), \
                    date_end=date(2022, 8, 2), weekday_int=1, repeat_timedelta_days=0), detailed=True \
            )  # 2 0-repeating meetings, no day match.
        (False, None)
        >>> meeting_conflict( \
            Meeting(time_start=time.min, time_end=time.max, date_start=date(2022, 8, 1), date_end=date(2022, 8, 15), \
                    weekday_int=0, repeat_timedelta_days=7), \
            Meeting(time_start=time(8, 0), time_end=time(10, 0), date_start=date(2022, 8, 15), \
                    date_end=date(2022, 8, 15), weekday_int=0, repeat_timedelta_days=0), detailed=True \
            )  # 1 0-repeating and 1 repeating meeting.
        (True, datetime.datetime(2022, 8, 15, 0, 0))
        >>> meeting_conflict( \
            Meeting(time_start=time(8, 0), time_end=time(10, 0), date_start=date(2022, 8, 1), \
                    date_end=date(2022, 8, 15), weekday_int=0, repeat_timedelta_days=7), \
            Meeting(time_start=time(10, 0), time_end=time(12, 0), date_start=date(2022, 8, 15), \
                    date_end=date(2022, 8, 15), weekday_int=0, repeat_timedelta_days=0), detailed=True \
            )  # 1 0-repeating and 1 repeating meeting.
        (False, None)
        >>> meeting_conflict( \
            Meeting(time_start=time.min, time_end=time.max, date_start=date(2022, 8, 1), date_end=date(2022, 8, 15), \
                    weekday_int=0, repeat_timedelta_days=7), \
            Meeting(time_start=time.min, time_end=time.max, date_start=date(2022, 8, 2), date_end=date(2022, 8, 16), \
                    weekday_int=1, repeat_timedelta_days=7), detailed=True \
            )  # 2 repeating meetings, no day match.
        (False, None)
        >>> meeting_conflict( \
            Meeting(time_start=time(8, 0), time_end=time(10, 0), date_start=date(2022, 8, 1), \
                    date_end=date(2022, 8, 15), weekday_int=0, repeat_timedelta_days=7), \
            Meeting(time_start=time(11, 0), time_end=time(12, 0), date_start=date(2022, 8, 1), \
                    date_end=date(2022, 8, 15), weekday_int=0, repeat_timedelta_days=7), detailed=True \
            )  # 2 repeating meetings, no time match.
        (False, None)
        >>> meeting_conflict( \
            Meeting(time_start=time(8, 0), time_end=time(10, 0), date_start=date(2022, 8, 1), \
                    date_end=date(2022, 8, 1), weekday_int=0, repeat_timedelta_days=0), \
            Meeting(time_start=time(8, 0), time_end=time(10, 0), date_start=date(2022, 8, 2), \
                    date_end=date(2022, 8, 2), weekday_int=1, repeat_timedelta_days=0), detailed=True \
            )  # 2 0-repeating meetings, no day match.
        (False, None)
        >>> meeting_conflict( \
            Meeting(time_start=time(8, 0), time_end=time(10, 0), date_start=date(2022, 8, 1), \
                    date_end=date(2022, 8, 1), weekday_int=0, repeat_timedelta_days=0), \
            Meeting(time_start=time(8, 30), time_end=time(9, 0), date_start=date(2022, 8, 1), \
                    date_end=date(2022, 8, 1), weekday_int=0, repeat_timedelta_days=0), detailed=True \
            )  # 2 0-repeating meetings.
        (True, datetime.datetime(2022, 8, 1, 8, 30))
        >>> meeting_conflict( \
            Meeting(time_start=time(9, 0), time_end=time(10, 0), date_start=date(2023, 5, 1), \
                    date_end=date(2023, 5, 1), weekday_int=0, repeat_timedelta_days=0), \
            Meeting(time_start=time(9, 10), time_end=time(11, 0), date_start=date(2023, 6, 26), \
                    date_end=date(2023, 8, 4), weekday_int=0, repeat_timedelta_days=7), detailed=True \
            )  # 2 0-repeating meetings.
        (False, None)
    """

    # TEST CODE ########################################################################################################
    # def __dev_print(title: str | None = None, lines: list[list[float, float, float, float]] | None = None,
    #                 points: list[list[float, float]] | None = None):
    #     """
    #     Args:
    #         lines: List of lines as 2 coordinates [x1, y1, x2, y2].
    #         points: List of points as a coordinate [x, y]
    #
    #     Returns:
    #
    #     """
    #     if lines is None:
    #         lines = []
    #     if points is None:
    #         points = []
    #
    #     point_markers = ['.', ',', 'o', 'v', '^', '<', '>', '1', '2', '3', '4', '8', 's', 'p', 'P', '*', 'h', 'H',
    #                      '+', 'x', 'X', 'D', 'd', '|', '_']
    #
    #     plt.title(str(title))
    #     plt.xlabel("X-axis: repeat_timedelta_days")  # Set the x-axis labels.
    #     plt.ylabel("Y-axis: UNIX Epoch Time")  # Set the y-axis labels.
    #
    #     for i, line in enumerate(lines):  # Plot lines.
    #         m = (line[3] - line[1]) / (line[2] - line[0])
    #         b = line[1] - m * line[0]
    #         if i % 2 != 0:
    #             plt.plot([line[0], line[2]], [line[1], line[3]], label=f"Line {i + 1}: y = {m}x + {b}")
    #         else:
    #             plt.plot([line[0], line[2]], [line[1], line[3]], label=f"Line {i + 1}: y = {m}x + {b}",
    #                      linestyle="dashed")
    #
    #     for i, point in enumerate(points):  # Plot points.
    #         plt.plot(point[0], point[1], point_markers[i % len(point_markers)],
    #                  label=f"Point {i + 1}: ({point[0]}, {point[1]})")
    #         plt.text(point[0], point[1], f"{i + 1}")
    #
    #     if lines or points:  # Call legend only if there is anything to put on the legend.
    #         plt.legend()
    #
    #     plt.show()
    # TEST CODE ########################################################################################################

    def __is_valid_date_intersection(poi_x: float | None = None, poi_y: float | None = None):
        """Final check for if a line-line point of intercept is of a valid date with meetings running."""

        if poi_x is not None and poi_y is not None:
            # mt1:
            if mt_1.repeat_timedelta_days == 0:  # Prevent ZeroDivisionError from doing n % 0.
                ts_1 = datetime.combine(mt_1.get_actual_date_start(), time.min).timestamp()
            elif poi_x % mt_1.repeat_timedelta_days == 0:
                ts_1 = (datetime.combine(mt_1.get_actual_date_start(), time.min) + timedelta(days=poi_x)).timestamp()
            else:
                return False
            # mt2:
            if mt_2.repeat_timedelta_days == 0:  # Prevent ZeroDivisionError from doing n % 0.
                ts_2 = datetime.combine(mt_2.get_actual_date_start(), time.min).timestamp()
            elif poi_x % mt_2.repeat_timedelta_days == 0:
                ts_2 = (datetime.combine(mt_2.get_actual_date_start(), time.min) + timedelta(days=poi_x)).timestamp()
            else:
                return False

            if poi_y == ts_1 == ts_2:
                return True
        return False

    # ------------------------------ 1. Test for time conflict. ------------------------------
    mt_1_t_s = mt_1.time_start
    mt_1_t_e = mt_1.time_end
    mt_2_t_s = mt_2.time_start
    mt_2_t_e = mt_2.time_end

    if not (mt_1_t_s <= mt_2_t_s < mt_1_t_e or mt_1_t_s < mt_2_t_e <= mt_1_t_e or mt_2_t_s <= mt_1_t_s < mt_2_t_e
            or mt_2_t_s < mt_1_t_e <= mt_2_t_e):
        # TEST CODE ####################################################################################################
        # __dev_print(title="FAILED Time Conflict")
        # TEST CODE ####################################################################################################
        return (False, None) if detailed else False

    # ------------------------------ 2. Test for date conflict. ------------------------------
    # x, y = (repeat_timedelta_days, timestamp of date_start with time.min used)
    # mt1:
    x1, y1 = (0, datetime.combine(mt_1.get_actual_date_start(), time.min).timestamp())
    x2, y2 = ((mt_1.get_actual_date_end() - mt_1.get_actual_date_start()).days,
              datetime.combine(mt_1.get_actual_date_end(), time.min).timestamp())
    # mt2:
    x3, y3 = (0, datetime.combine(mt_2.get_actual_date_start(), time.min).timestamp())
    x4, y4 = ((mt_2.get_actual_date_end() - mt_2.get_actual_date_start()).days,
              datetime.combine(mt_2.get_actual_date_end(), time.min).timestamp())

    if mt_1.repeat_timedelta_days == 0 and mt_2.repeat_timedelta_days == 0:
        # 2 no-repeat meetings -> 2 point match test.

        if y1 == y2 == y3 == y4:
            # TEST CODE ################################################################################################
            # __dev_print(title="Point-Point Match", points=[[x1, y1], [x3, y3]])
            # TEST CODE ################################################################################################
            return (True, datetime.combine(mt_1.get_actual_date_start(), max(mt_1.time_start, mt_2.time_start))) \
                if detailed else True
            # Given we know a conflict exists, we can use max time_start, this gives the earliest conflict time.
        else:
            # TEST CODE ################################################################################################
            # __dev_print(title="FAILED Point-Point Match", points=[[x1, y1], [x3, y3]])
            # TEST CODE ################################################################################################
            return (False, None) if detailed else False

    elif (mt_1.repeat_timedelta_days == 0 and y1 == y2) or (mt_2.repeat_timedelta_days == 0 and y3 == y4):
        # 1 repeating meeting + 1 no-repeat meeting -> line and horizontal line intercept test.
        # The or in the if statement above will be a xor since the previous if statement will catch the inclusive cases.

        # Convert the no-repeat meeting to a horizontal line by adjusting x values.
        if mt_1.repeat_timedelta_days == 0:
            x1, x2, = 0, max(x3, x4)
        else:  # mt_2.repeat_timedelta_days == 0
            x3, x4 = 0, max(x1, x2)

    # 1 repeating meeting + 1 no-repeat meeting -> line and horizontal line intercept test -> 2 line intercept test.
    # 2 repeating meetings -> 2 line intercept test.

    # Calculate slopes and y-shifts.
    m1 = (y2 - y1) / (x2 - x1)
    b1 = y1 - m1 * x1
    m2 = (y4 - y3) / (x4 - x3)
    b2 = y3 - m2 * x3

    if m1 == m2:  # 2 parallel lines.
        if b1 == b2:
            # Overlapping lines, complete intersection.
            # TEST CODE ################################################################################################
            # __dev_print(title="OVERLAPPING Line-Line Intersect", lines=[[x1, y1, x2, y2], [x3, y3, x4, y4]])
            # TEST CODE ################################################################################################
            return (True, None) if detailed else True
        # TEST CODE ####################################################################################################
        # else:
        #     __dev_print(title="PARALLEL (FAILED) Line-Line Intersect", lines=[[x1, y1, x2, y2], [x3, y3, x4, y4]])
        # TEST CODE ####################################################################################################

    else:  # 2 non-parallel lines.
        x = (b2 - b1) / (m1 - m2)

        if not (x < min(x1, x2) or x > max(x1, x2) or x < min(x3, x4) or x > max(x3, x4)):
            # Lines have an intersect.
            y = y1 + ((y2 - y1) / (x2 - x1)) * (x - x1)
            if __is_valid_date_intersection(x, y):
                # TEST CODE ############################################################################################
                # __dev_print(title="Line-Line Intersect", lines=[[x1, y1, x2, y2], [x3, y3, x4, y4]],
                #             points=[[x, y]])
                # TEST CODE ############################################################################################
                return (True, datetime.fromtimestamp(y)) if detailed else True
        # TEST CODE ####################################################################################################
        #     else:
        #         __dev_print(title="FALSE Line-Line Intersect", lines=[[x1, y1, x2, y2], [x3, y3, x4, y4]],
        #                     points=[[x, y]])
        # else:
        #     __dev_print(title="FAILED Line-Line Intersect", lines=[[x1, y1, x2, y2], [x3, y3, x4, y4]])
        # TEST CODE ####################################################################################################

    return (False, None) if detailed else False
