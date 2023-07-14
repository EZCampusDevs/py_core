"""CourseOptimizerCriteria defines the criteria for the course_level_optimizer to calculate the rating value of a
single Course object.
"""

from datetime import time
from typing import Optional

from pydantic import BaseModel

from .course_class import Course


class CourseOptimizerCriteria(BaseModel):
    """
    times_start: List of the earliest allowed start time per day.
        Follows datetime.datetime.weekday() index convention (0 = Monday, 1 = Tuesday, ..., 6 = Sunday).
        Use case: User wants to ensure they start school after a certain time each day.
    times_start_weight:
    times_end: List of the latest allowed end time per day.
        Follows datetime.datetime.weekday() index convention (0 = Monday, 1 = Tuesday, ..., 6 = Sunday).
        Use case: User wants to ensure they get off from school by a certain time each day.
    times_end_weight:
    is_virtual: True = prioritize virtual classes, False = prioritize in-person classes.
        Use case: User wants more virtual (or in-person) classes.
    is_virtual_weight:
    high_prof_rating: Minimum professor rating.
        Should be within range [0, 1], logically a 0 rating would be the same as None.
        Use case: User wants to get actually decent profs.
    high_prof_rating_weight:
    min_seats_open: Minimum number of seats open for registration.
        Use case: User wants to ensure they will have open seats to be able to register.
    min_seats_open_weight:
    maximum_enrollment: Maximum capacity size.
        Use case: User wants smaller class sizes.
    maximum_enrollment_weight:

    Notes:
        The None state means that no criteria specified.

    Examples:
        >>> from datetime import date, time
        >>> CourseOptimizerCriteria( \
        available_times=[[1, time(10, 0), time(12, 30)]], \
        available_times_weight=0.3, \
        high_prof_rating=True, \
        high_prof_rating_weight=0.5, \
        max_capacity=1, \
        max_capacity_weight=0.2)
    """

    # Note all the defaults for criteria is None, except for available_times
    # which defaults to an empty list.
    available_times: list[tuple[int, time, time]] = []  # Default empty list
    # available_times = [[weekday_int, time_start, time_end], ...]
    available_times_weight: float = 0.0
    is_virtual: Optional[bool]  # None, True or False
    is_virtual_weight: float = 0.0
    high_prof_rating: Optional[bool]  # None, True or False
    high_prof_rating_weight: float = 0.0
    min_seats_open: Optional[int]  # None or int
    min_seats_open_weight: float = 0.0
    max_capacity: Optional[int]  # None or int
    max_capacity_weight: float = 0.0

    def total_weights(self) -> float:
        return sum(
            [
                self.available_times_weight,
                self.is_virtual_weight,
                self.high_prof_rating_weight,
                self.min_seats_open_weight,
                self.max_capacity_weight,
            ]
        )

    def course_eval(self, course: Course) -> float:
        """Evaluates the rating of a Course object for schedule optimizer.
        Higher rating means a more favourable course.

        Args:
            course: Course object of which to calculate the rating/weight for.

        Returns:
            Rating/weight float.
        """
        rating = 0.0
        general_multiplier = 1
        if self.available_times and self.available_times_weight > 0:
            general_multiplier += 0.25
            for sub in self.available_times:
                for mt in course.class_time:
                    if sub[0] in mt.decode_days_of_week().values() and (
                        sub[1] <= mt.time_start <= sub[2] or sub[1] <= mt.time_end <= sub[2]
                    ):
                        # TODO(Daniel): This is an inaccurate representation ^^^!
                        #  Use some form of linear or function based rating scaling representing what percentage of a
                        #  meeting is within/outside the rating available_times criteria.
                        rating += mt.num_actual_meetings() * self.available_times_weight
        if self.is_virtual is not None and self.is_virtual_weight > 0:
            if self.is_virtual == course.is_virtual:
                general_multiplier += 0.25
                rating += 10 * course.num_actual_meetings() * self.is_virtual_weight
        # Notice available_times and is_virtual ratings depend on the
        # actual meetings count. This is to help account for variations of
        # meeting counts. For example, a user wants virtual classes (Optimizer
        # criteria is_virtual=True) as they don't want to commute to campus as
        # much. Suppose the optimizer is forced to decide between a biweekly
        # in-person lab versus a weekly in-person lecture. It will rate the
        # biweekly lab to be higher (more favourable) than the weekly lecture
        # because it has more meetings.
        if self.high_prof_rating is not None and self.high_prof_rating_weight > 0:
            if self.high_prof_rating:
                instructor_rating = sum([f.rating for f in course.instructors])
                if instructor_rating is not None:
                    general_multiplier += 0.25
                    rating += instructor_rating * 100 * self.high_prof_rating_weight
        if self.min_seats_open is not None and self.min_seats_open_weight > 0:
            if self.min_seats_open <= (course.maximum_enrollment - course.current_enrollment):
                general_multiplier += 0.25
                rating += 100 * self.min_seats_open_weight
        if self.max_capacity is not None and self.max_capacity > 0:
            if self.max_capacity >= course.maximum_enrollment:
                general_multiplier += 0.25
                rating += 100 * self.max_capacity_weight
        rating *= general_multiplier
        return rating
