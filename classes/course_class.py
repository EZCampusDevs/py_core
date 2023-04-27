"""Course class module.

The Course class and by extension the module's functions represent universal course structures and data values.
"""

from typing import Optional, List

from pydantic import BaseModel, root_validator

from classes.extended_meeting_class import ExtendedMeeting
from classes.meeting_class import Meeting, meetings_are_time_valid


class Course(BaseModel):
    """Course class defines a single general course identified by a CRN (course registration number).

    fac: Faculty ID identifying faculty department. (Example: "MATH").
    uid: (UID = University ID). ID code ending with 'U'. (Example: "1020U").
    crn: (CRN = Course Registration Number). A unique int that represents each course. (Example: 12345).
    class_type: Identifies the type of class. (Example: "Lecture", "Tutorial" & "Laboratory").
    title: Title of the class. (Example: "Calculus II").
    section: Section identifier, usually a number with possible leading zeros. (Example: "001").
    class_time: List of Meeting objects. (meeting_class.py).
    is_linked: Defines if the class has any linked classes that are required.
    link_tag: Identifies the link type for its c. (Example: "A1").
        For computation, links are made with matching tags from classes with the same fac and uid. Class with a
        link_tag="A1" needs to link with another class of link_tag="B#", where # is an integer.
    seats_filled: Number of seats filled.
    max_capacity: Maximum capacity of a course.
    instructor: Course's instructor's name.
    instructor_email: Course's instructor's email.
    instructor_rating: Course's instructor's rating.
    is_virtual: Defines if the class is completely virtual/online.
    is_restricted: Defines if the class has any restrictions.
    restrictions: Restrictions in a string format.

    Examples:
        >>> from datetime import date, time
        >>> Course(fac="MATH", \
                uid="1234U", \
                crn=12345, \
                class_type="Lecture", \
                title="Calculus 9000", \
                section="003", \
                class_time=[ \
                    Meeting( \
                        time_start=time(9, 40), \
                        time_end=time(11, 0), \
                        weekday_int=0, \
                        date_start=date(2022, 1, 17), \
                        date_end=date(2022, 4, 14), \
                        repeat_timedelta_days=7, \
                        location="UOW SYN SYN" \
                    ), \
                    Meeting( \
                        time_start=time(9, 40), \
                        time_end=time(11, 0), \
                        weekday_int=3, \
                        date_start=date(2022, 1, 17), \
                        date_end=date(2022, 4, 14), \
                        repeat_timedelta_days=7, \
                        location="UON SPY SPY9999", \
                    ) \
                ], \
                is_linked=True, \
                link_tag="A1", \
                seats_filled=6, \
                max_capacity=100, \
                instructor="Last, First", \
                instructor_email="First.Last@ontariotechu.ca", \
                instructor_rating=0.84, \
                is_virtual=False, \
                restrictions={ \
                    'Not all restrictions are applicable.': [], \
                    'Must be enrolled in one of the following Levels: ': \
                        ['Undergraduate (UG)'], \
                    'Must be enrolled in one of the following Colleges: ': \
                        ['Engineering & Applied Science (50)'], \
                    'Must be enrolled in one of the following Classes: ': \
                        ['First year (Y1)'], \
                    'Cannot be enrolled in one of the following Majors: ': \
                        [ \
                            'Cool Science (COOL)', \
                            'Integrative Awesomescience (ASCI)' \
                        ] \
                })
        Course(fac='MATH', uid='1234U', crn=12345, class_type='Lecture', title='Calculus 9000', section='003', class_time=[Meeting(time_start=datetime.time(9, 40), time_end=datetime.time(11, 0), weekday_int=0, date_start=datetime.date(2022, 1, 17), date_end=datetime.date(2022, 4, 14), repeat_timedelta_days=7, location='UOW SYN SYN'), Meeting(time_start=datetime.time(9, 40), time_end=datetime.time(11, 0), weekday_int=3, date_start=datetime.date(2022, 1, 17), date_end=datetime.date(2022, 4, 14), repeat_timedelta_days=7, location='UON SPY SPY9999')], is_linked=True, link_tag='A1', seats_filled=6, max_capacity=100, instructor='Last, First', instructor_email='First.Last@ontariotechu.ca', instructor_rating=0.84, is_virtual=False, restrictions={'Not all restrictions are applicable.': [], 'Must be enrolled in one of the following Levels: ': ['Undergraduate (UG)'], 'Must be enrolled in one of the following Colleges: ': ['Engineering & Applied Science (50)'], 'Must be enrolled in one of the following Classes: ': ['First year (Y1)'], 'Cannot be enrolled in one of the following Majors: ': ['Cool Science (COOL)', 'Integrative Awesomescience (ASCI)']})
    """
    fac: str
    uid: str
    crn: int
    class_type: str
    title: str
    section: Optional[str]
    class_time: List[Meeting] = []
    is_linked: bool
    link_tag: Optional[str]
    seats_filled: int
    max_capacity: int
    instructor: Optional[str]
    instructor_email: Optional[str]
    instructor_rating: Optional[float]
    is_virtual: bool
    restrictions: Optional[dict]

    @root_validator()
    def verify_valid_instructor_rating(cls, values):
        rt = values.get("instructor_rating")
        if rt is not None and not isinstance(rt, float):
            raise ValueError(f"Expected type <None> or <float>, got {type(rt)}")
        if isinstance(rt, float) and not (0 <= rt <= 1):
            raise ValueError(f"With <float> expected 0 <= instructor_rating <= 1, got instructor_rating={rt}")
        return values

    def course_code(self) -> str:
        """Get the general course code of the Course object.

        Returns:
            Course code.
        """
        return f"{self.fac}{self.uid}"

    def get_comp_key(self) -> str:
        """Get representative value of course and type used for computation.

        Returns:
            A Course object's manifest representative value.

        Notes:
            Used in special computations such as schedule optimization and event planning.
        """
        representation = f"{self.course_code()} {self.class_type}"
        # Alternative representation:
        # representation = (f"{course.course_code()} {course.link_tag[0]}"
        #                   if course.link_tag is not None
        #                   else f"{course.course_code()} None")
        return representation

    def num_actual_meetings(self) -> int:
        """Get the total number of times a course meeting actually occurs (sum of meeting's reoccurrence).

        Returns:
            Total number of times a course's class meets.

        Notes:
            Potential logic error due to bad data in of self.date_start and self.date_end. See:
            Meeting.num_actual_meetings() documentation.
        """
        count = 0
        for meeting in self.class_time:
            count += meeting.num_actual_meetings()
        return count

    def get_raw_str(self):
        """For prototyping purposes only.

        Returns:
            Default str similar to regular __str__ methods.
        """
        return (f"fac={self.fac}\n"
                f"uid={self.uid}\n"
                f"crn={self.crn}\n"
                f"class_type={self.class_type}\n"
                f"title={self.title}\n"
                f"section={self.section}\n"
                f"class_time={self.class_time}\n"
                f"is_linked={self.is_linked}\n"
                f"link_tag={self.link_tag}\n"
                f"seats_filled={self.seats_filled}\n"
                f"max_capacity={self.max_capacity}\n"
                f"instructor={self.instructor}\n"
                f"instructor_email={self.instructor_email}\n"
                f"instructor_rating={self.instructor_rating}\n"
                f"is_virtual={self.is_virtual}\n"
                f"restrictions={self.restrictions}")

    def __str__(self):
        return self.get_raw_str()


def schedule_is_time_valid(course_list: list[Course]) -> bool:
    """Determines if a list of Course objects (schedule) is has time conflicts.

    Args:
        course_list: List of course objects

    Returns:
        True if a schedule has no time conflicts, False if time conflicts exist.
    """
    if not course_list:  # Empty list
        return True
    mt_list = []
    for course in course_list:
        mt_list += course.class_time
    return meetings_are_time_valid(mt_list=mt_list)


def get_min_students_of_courses(courses: list[Course]) -> int:
    """Get minimum number of unique students registered in a list of courses.

    Args:
        courses: List of courses to process.

    Returns:
        The theoretical min number of unique students registered for courses.

    Notes:
        This is meant to be called for completely internal uses only.
    """
    if not courses:  # If there are no courses return 0.
        return 0
    max_by_class_type = {}  # Max students by course and class type (comp_key).
    for c in courses:
        if c.get_comp_key() in max_by_class_type.keys():
            max_by_class_type[c.get_comp_key()] += c.seats_filled
        else:
            max_by_class_type[c.get_comp_key()] = c.seats_filled
    return min(max_by_class_type.values())


def merge_all_restrictions(course_list: list[Course]) -> dict:
    """Get all restrictions merged from a list of Course objects.

    Args:
        course_list: List of course objects to merge restrictions of.

    Returns:
        Restrictions represented as dict.
    """
    all_restrictions = {}
    for c in course_list:
        for r_type, r_list in c.restrictions.items():
            if r_type not in list(all_restrictions.keys()):  # Type not added
                # as a key to the total dict yet.
                all_restrictions[r_type] = r_list  # Add new type as a key and
                # value is the entire sub list to the total dict.
            else:  # Type already exists as an r_type on the total dict.
                all_restrictions[r_type] = list(set(all_restrictions[r_type] + r_list))
                # Add missing restrictions in the value's sub list.
    return all_restrictions


def schedule_to_simplified_json(course_list: list[Course]) -> list[dict]:
    """Converts a list of Course objects (schedule) to a simplified json list.

    Args:
        course_list: List of course objects.

    Returns:
        json list of dicts of the schedule.
    """
    schedule = []
    for c in course_list:
        new_event = {
            "title":
                f"{c.title} {c.class_type[:3].upper()} ({c.course_code()})",
            "description":
                f"Instructor: {c.instructor}\n"
                f"Instructor email: {c.instructor_email}\n"
                f"Instructor rating: {c.instructor_rating}\n"
                f"CRN: {c.crn}\n"
                f"Section: {c.section}\n"
                f"Seats filled: {c.seats_filled}\n"
                f"Max capacity: {c.max_capacity}\n"
                f"Registration restrictions: {c.restrictions}",
            "meetings": [
                {
                    "time_start": mt.time_start.isoformat(),
                    "time_end": mt.time_end.isoformat(),
                    "weekday_int": mt.weekday_int,
                    "date_start": mt.get_actual_date_start().isoformat(),
                    "date_end": mt.get_actual_date_end().isoformat(),
                    # Notice here unlike the format using by the backend logic, it is sending the simplified actual
                    # date starts and ends
                    "repeat_timedelta_days": mt.repeat_timedelta_days,
                    "location": mt.location
                } for mt in c.class_time
            ]
        }
        schedule.append(new_event)
    return schedule


def course_to_extended_meetings(course_list: list[Course]) -> list[ExtendedMeeting]:
    """Translate a list of Course objects to list of ExtendedMeetings

    Args:
        course_list: List of course objects.

    Returns:
        List of translated ExtendedMeeting objects.
    """

    def instructor_details(course: Course) -> str:
        if isinstance(course.instructor, str):
            if isinstance(course.instructor_rating, float):
                return f"{course.instructor} ({course.instructor_email}) {round(c.instructor_rating * 100)}%"
                # TODO(Daniel): Warning! The above code assumes we will have the instructor email if we have the
                #  instructor name.
            else:
                return f"{course.instructor} ({course.instructor_email})"
        else:  # course.instructor is None.
            return "Unspecified"

    ex_mt_list = []
    for c in course_list:
        ex_mt_list += [
            ExtendedMeeting(
                time_start=mt.time_start,
                time_end=mt.time_end,
                weekday_int=mt.weekday_int,
                date_start=mt.date_start,
                date_end=mt.date_end,
                repeat_timedelta_days=mt.repeat_timedelta_days,
                location="VIRTUAL" if c.is_virtual else str(mt.location),
                name=f"{c.title} {c.class_type[:3].upper()} ({c.course_code()})",
                description=(
                    f"Instructor: {instructor_details(course=c)}\n"
                    f"CRN: {c.crn}\n"
                    f"Section: {c.section}\n"
                    f"Has linked classes: {c.is_linked}"
                ),
                seats_filled=c.seats_filled,
                max_capacity=c.max_capacity,
                is_virtual=c.is_virtual
            ) for mt in c.class_time
        ]
    return ex_mt_list
