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
Course related DML abstraction.
"""

from datetime import datetime

from sqlalchemy import (
    and_,
    not_,
    or_,
)
from sqlalchemy.orm.session import Session as SessionObj

import logging

from . db import Session, SessionObj
from . db import db_globals as DG
from . db import db_tables as DT

from . classes.user_classes import BasicUser
from .classes.course_class import Course, merge_course_meeting_occurrences
from .classes.instructor_class import Instructor
from .classes.meeting_class import Meeting


def get_courses_via(
    course_data_id_list: list[int] | None = None,
    course_id_list: list[int] | None = None,
) -> list[Course]:
    """Get a list of Course objects based on search parameters.

    Args:
        course_data_id_list: Individual Course (CRN) data ids.
        course_id_list: Course (code) ids.

    Returns:
        List of Course objects based on search parameters.
    """
    if (not course_data_id_list or course_data_id_list is None) and (
        not course_id_list or course_id_list is None
    ):
        return []

    if course_data_id_list is None:
        course_data_id_list = []
    if course_id_list is None:
        course_id_list = []

    session: SessionObj
    try:
        with DG.Session.begin() as session:
            course_list = __query_courses(
                session=session,
                course_data_id_list=course_data_id_list,
                course_id_list=course_id_list,
            )
            return [merge_course_meeting_occurrences(c) for c in course_list]
    except AttributeError as e:
        msg = e.args[0]
        if "'NoneType' object has no attribute 'begin'" in msg:
            raise RuntimeWarning(
                f"{msg} <--- Daniel: Check (local / ssh) connection to DB, possible missing "
                f"init_database() call via 'from py_core.db import init_database'"
            )
        else:
            raise e
    except Exception as e:
        raise e


def get_course_ids(course_codes: list[str], term_id: int) -> list[int]:
    """Get a list of course ids based on a list of course codes.

    Args:
        term_id: Term id to define scope.
        course_codes: List of course codes to look up.

    Returns:
        List of course ids.
    """

    try:

        session: SessionObj
        with Session().begin() as session:

            c_d_result = (
                session.query(DT.TBL_Course)
                .filter(
                    and_(DT.TBL_Course.course_code.in_(course_codes), DT.TBL_Course.term_id == term_id)
                )
                .all()
            )

            return [result.course_id for result in c_d_result]

    except AttributeError as e:

        msg = e.args[0]

        if "'NoneType' object has no attribute 'begin'" in msg:
            raise RuntimeWarning(
                f"{msg} <--- Daniel: Check (local / ssh) connection to DB, possible missing "
                f"init_database() call via 'from py_core.db import init_database'"
            )

        raise e


def __query_courses(
    session: SessionObj, course_data_id_list: list[int], course_id_list: list[int]
) -> list[Course]:
    # TODO(Daniel): I must have been on something or super sleep deprived when I wrote this... Lol
    #  no joins in query searches??!! I will fix this when I get a chance. Should still work tho.
    course_list = []

    # Course data result looking for matches of course_data_id and course_id, but also making
    #  sure there are no duplicates in the query.
    c_d_result = (
        session.query(DT.TBL_Course_Data)
        .filter(
            or_(
                DT.TBL_Course_Data.course_data_id.in_(course_data_id_list),
                and_(
                    not_(DT.TBL_Course_Data.course_data_id.in_(course_data_id_list)),
                    DT.TBL_Course_Data.course_id.in_(course_id_list),
                ),
            )
        )
        .all()
    )

    for c_d_r in c_d_result:
        # Meeting result matching the previous query's course_data_id.
        mt_result = (
            session.query(DT.TBL_Meeting)
            .filter(DT.TBL_Meeting.course_data_id == c_d_r.course_data_id)
            .all()
        )

        meeting_list = []

        for mt_r in mt_result:

            if mt_r.begin_time is not None and mt_r.end_time is not None:

                timezone_str = (
                    session.query(DT.TBL_School)
                    .join(DT.TBL_Term)
                    .filter(DT.TBL_Term.term_id == mt_r.term_id)
                    .first()
                ).timezone

                meeting_list.append(
                    Meeting(
                        time_start=datetime.strptime(str(mt_r.begin_time), "%H%M").time(),
                        time_end=datetime.strptime(str(mt_r.end_time), "%H%M").time(),
                        date_start=mt_r.start_date,
                        date_end=mt_r.end_date,
                        timezone_str=timezone_str,
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
            session.query(DT.TBL_Course_Faculty.faculty_id)
            .filter(DT.TBL_Course_Faculty.course_data_id == c_d_r.course_data_id)
            .all()
        )
        faculty_list = []
        for c_fc_r in c_fc_result:
            fc_result = (
                session.query(DT.TBL_Faculty)
                .filter(DT.TBL_Faculty.faculty_id == c_fc_r.faculty_id)
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
                course_code=session.query(DT.TBL_Course)
                .filter(DT.TBL_Course.course_id == c_d_r.course_id)
                .first()
                .course_code,
                title=c_d_r.course_title,
                crn=c_d_r.crn,
                class_type=(
                    session.query(DT.TBL_Class_Type.class_type)
                    .filter(DT.TBL_Class_Type.class_type_id == c_d_r.class_type_id)
                    .first()
                ).class_type,
                section=c_d_r.sequence_number,
                subject=(
                    session.query(DT.TBL_Subject.subject)
                    .filter(DT.TBL_Subject.subject_id == c_d_r.subject_id)
                    .first()
                ).subject,
                subject_long=(
                    session.query(DT.TBL_Subject.subject_long)
                    .filter(DT.TBL_Subject.subject_id == c_d_r.subject_id)
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
    return course_list
