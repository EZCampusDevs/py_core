from datetime import datetime

from sqlalchemy import (
    and_,
    not_,
    or_,
)
from sqlalchemy.orm.session import Session as SessionObj

from . import db_globals as DG
from .db_tables import (
    TBL_Course_Data,
    TBL_Meeting,
    TBL_Course_Faculty,
    TBL_Faculty,
    TBL_Course,
    TBL_Class_Type,
    TBL_Subject,
)
from ..classes.course_class import Course, merge_course_meeting_occurrences
from ..classes.instructor_class import Instructor
from ..classes.meeting_class import Meeting


def get_courses_via(
    course_data_id_list: list[int] | None = None,
    course_id_list: list[int] | None = None,
) -> list[Course]:
    if (not course_data_id_list or course_data_id_list is None) and (
        not course_id_list or course_id_list is None
    ):
        return []

    if course_data_id_list is None:
        course_data_id_list = []
    if course_id_list is None:
        course_id_list = []

    course_list = []
    session: SessionObj
    with DG.Session.begin() as session:
        c_d_result = (
            session.query(TBL_Course_Data)
            .filter(
                or_(
                    TBL_Course_Data.course_data_id.in_(course_data_id_list),
                    and_(
                        not_(TBL_Course_Data.course_data_id.in_(course_data_id_list)),
                        TBL_Course_Data.course_id.in_(course_id_list),
                    ),
                )
            )
            .all()
        )
        for c_d_r in c_d_result:
            mt_result = (
                session.query(TBL_Meeting)
                .filter(TBL_Meeting.course_data_id == c_d_r.course_data_id)
                .all()
            )
            meeting_list = []
            for mt_r in mt_result:
                if mt_r.begin_time is not None and mt_r.end_time is not None:
                    meeting_list.append(
                        Meeting(
                            time_start=datetime.strptime(str(mt_r.begin_time), "%H%M").time(),
                            time_end=datetime.strptime(str(mt_r.end_time), "%H%M").time(),
                            date_start=mt_r.start_date,
                            date_end=mt_r.end_date,
                            occurrence_unit=None,
                            # TODO: Temporary hardcode, needs to be calculated at scraper level.
                            occurrence_interval=None,
                            # TODO: Temporary hardcode, needs to be calculated at scraper level.
                            occurrence_limit=None,
                            # TODO: Temporary hardcode, needs to be calculated at scraper level.
                            days_of_week=mt_r.days_of_week,
                            location=f"{c_d_r.campus_description} {mt_r.building} {mt_r.room}",
                        )
                    )
            c_fc_result = (
                session.query(TBL_Course_Faculty.faculty_id)
                .filter(TBL_Course_Faculty.course_data_id == c_d_r.course_data_id)
                .all()
            )
            faculty_list = []
            for c_fc_r in c_fc_result:
                fc_result = (
                    session.query(TBL_Faculty)
                    .filter(TBL_Faculty.faculty_id == c_fc_r.faculty_id)
                    .first()
                )
                faculty_list.append(
                    Instructor(
                        faculty_id=fc_result.faculty_id,
                        name=fc_result.instructor_name,
                        email=fc_result.instructor_email,
                        rating=fc_result.instructor_rating,
                    )
                )
            course_list.append(
                Course(
                    course_code=session.query(TBL_Course)
                    .filter(TBL_Course.course_id == c_d_r.course_id)
                    .first()
                    .course_code,
                    title=c_d_r.course_title,
                    crn=c_d_r.crn,
                    class_type=(
                        session.query(TBL_Class_Type.class_type)
                        .filter(TBL_Class_Type.class_type_id == c_d_r.class_type_id)
                        .first()
                    ).class_type,
                    section=c_d_r.sequence_number,
                    subject=(
                        session.query(TBL_Subject.subject)
                        .filter(TBL_Subject.subject_id == c_d_r.subject_id)
                        .first()
                    ).subject,
                    subject_long=(
                        session.query(TBL_Subject.subject_long)
                        .filter(TBL_Subject.subject_id == c_d_r.subject_id)
                        .first()
                    ).subject_long,
                    class_time=meeting_list,
                    is_open_section=c_d_r.open_section,
                    is_section_linked=c_d_r.is_section_linked,
                    link_tag=c_d_r.link_identifier,
                    restrictions=None,
                    # TODO: Temporary hardcode, needs restrictions support at scraper level.
                    current_enrollment=c_d_r.current_enrollment,
                    maximum_enrollment=c_d_r.maximum_enrollment,
                    current_waitlist=c_d_r.current_waitlist,
                    maximum_waitlist=c_d_r.maximum_waitlist,
                    delivery=c_d_r.delivery,
                    is_virtual=True if "virtual" in c_d_r.delivery.lower() else False,
                    # TODO: This needs to be determined at scraper level ^.
                    campus_description=c_d_r.campus_description,
                    instructors=faculty_list,
                    credits=c_d_r.credit_hours,
                )
            )
    return [merge_course_meeting_occurrences(c) for c in course_list]
