"""Course class module.

The Course class and by extension the module's functions represent universal course structures and data values.
"""

from typing import Optional, List

from pydantic import BaseModel, validator

from .extended_meeting_class import ExtendedMeeting
from .instructor_class import Instructor
from .meeting_class import Meeting, meetings_conflict, merged_meeting_occurrences


class Course(BaseModel):
    """Course class defines a single general course identified by a CRN."""
    course_code: str  # Aka course code, example: "BIOL1020U".
    subject: Optional[str]  # Aka subject, example: "BIOL".
    subject_long: Optional[str]  # Aka subject long, example: "Biology".
    crn: int  # Aka course reference/registration number: 12345.
    class_type: str  # Aka class type, example: "Lecture".
    title: str  # Aka course title, example: "Biology II".
    section: Optional[str]  # Aka sequence number, example: "001".
    class_time: List[Meeting] = []  # Class times represented as a list of Meetings.
    is_linked: bool  # Aka is section linked.
    link_tag: Optional[str]  # Aka link identifier, example: "A1".
    seats_filled: int  # Aka enrollment.
    max_capacity: int  # Aka maximum enrollment.
    seats_available: Optional[int]  # Defaults if not provided. Aka enrollment seats available.
    is_virtual: bool
    restrictions: Optional[dict]  # JSON data for class registration restrictions.
    instructional_method: Optional[str]  # Non-essential (api forwarded) data.
    is_open: Optional[bool]  # Non-essential (api forwarded) data.
    wait_filled: Optional[int]  # Aka wait-list count. Non-essential (api forwarded) data.
    wait_capacity: Optional[int]  # Aka wait-list capacity. Non-essential (api forwarded) data.
    instructors: List[Instructor] = []  # Aka list of Instructor.

    @validator("seats_available", always=True)
    def confirm_seats_available(cls, v, values):
        if not isinstance(v, int):
            sf = values.get("seats_filled")
            mc = values.get("max_capacity")
            return mc - sf if mc - sf >= 0 else 0
        return v

    def get_comp_key(self) -> str:
        """Get representative value of course and type used for computation.

        Returns:
            A Course object's manifest representative value.

        Notes:
            Used in special computations such as schedule optimization and event planning.
        """
        return f"{self.course_code} {self.class_type}"

    def num_actual_meetings(self) -> int:
        """Get the total number of times a course meeting actually occurs (sum of meeting's reoccurrence).

        Returns:
            Total number of times a course's class meets.

        Notes:
            Potential logic error due to bad data in of self.date_start and self.date_end. See:
            Meeting.num_actual_meetings() documentation.
        """
        return sum([mt.num_of_occurrences() for mt in self.class_time])

    def faculty_instructors_text(self) -> str:
        return ", ".join(
            [" ".join(
                [
                    i.name,  # We always assume the instructor has name filled, else use the code below.
                    # i.name if isinstance(i.name, str) else '',
                    f"({i.email})" if isinstance(i.email, str) else '',
                    f"{f'{i.rating}/100' if isinstance(i.rating, int) else ''}"
                ]
            ) for i in self.instructors]
        ) if self.instructors else "N/A"


def schedule_time_conflicts(course_list: list[Course]) -> bool:
    """Determines if a list of Course objects (schedule) is has time conflicts.

    Args:
        course_list: List of course objects

    Returns:
        True if schedule has time conflicts, False if no time conflicts exist.
    """
    if not course_list:  # Empty list
        return True
    mt_list = []
    for course in course_list:
        mt_list += course.class_time
    return meetings_conflict(mt_list=mt_list)


def merge_course_meeting_occurrences(course: Course) -> Course:
    return Course(course_code=course.course_code, subject=course.subject, subject_long=course.subject_long,
                  crn=course.crn, class_type=course.class_type, title=course.title, section=course.section,
                  class_time=merged_meeting_occurrences(course.class_time), is_linked=course.is_linked,
                  link_tag=course.link_tag, seats_filled=course.seats_filled, max_capacity=course.max_capacity,
                  seats_available=course.seats_available, is_virtual=course.is_virtual,
                  restrictions=course.restrictions, instructional_method=course.instructional_method,
                  is_open=course.is_open, wait_filled=course.wait_filled, wait_capacity=course.wait_capacity,
                  instructors=course.instructors)


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


def course_to_extended_meetings(course_list: list[Course]) -> list[ExtendedMeeting]:
    """Translate a list of Course objects to list of ExtendedMeetings

    Args:
        course_list: List of course objects.

    Returns:
        List of translated ExtendedMeeting objects.
    """
    ex_mt_list = []
    for c in course_list:
        ex_mt_list += [
            ExtendedMeeting(
                time_start=mt.time_start,
                time_end=mt.time_end,
                date_start=mt.date_start,
                date_end=mt.date_end,
                occurrence_unit=mt.occurrence_unit,
                occurrence_interval=mt.occurrence_interval,
                occurrence_limit=mt.occurrence_limit,
                days_of_week=mt.days_of_week,
                location="VIRTUAL" if c.is_virtual else str(mt.location),
                name=f"{c.title} {c.class_type[:3].upper()} ({c.course_code})",
                description=(
                    rf"Instructor{'s' if len(c.instructors) > 1 else ''}: {c.faculty_instructors_text()}\n"
                    rf"CRN: {c.crn}\n"
                    rf"Section: {c.section}\n"
                    rf"Seats filled: {c.seats_filled}\n"
                    rf"Max capacity: {c.max_capacity}\n"
                    rf"Seats available: {c.seats_available}\n"
                    rf"Has linked classes: {c.is_linked}"
                ),
                seats_filled=c.seats_filled,
                max_capacity=c.max_capacity,
                is_virtual=c.is_virtual
            ) for mt in c.class_time
        ]
    return ex_mt_list
