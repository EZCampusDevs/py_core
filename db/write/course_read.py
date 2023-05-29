# TODO: Tables should probably get some column name standardization fix.

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy import event
from sqlalchemy.orm import sessionmaker, declarative_base

from ..course_tables import (TBL_Course, TBL_Course_Faculty, TBL_Meeting, TBL_Course_Data, TBL_Faculty, TBL_Class_Type)
from ...classes.course_class import Course
from ...classes.instructor_class import Instructor
from ...classes.meeting_class import Meeting

load_dotenv()

Engine = None
Session: sessionmaker = None
Base = declarative_base()


def init_database(use_mysql: bool = True, db_host: str = os.getenv("db_host"), db_port: str = os.getenv("db_port"),
                  db_name: str = os.getenv("db_name"), db_user: str = os.getenv("db_user"),
                  db_pass: str = os.getenv("db_pass"), db_directory: str = os.getenv("db_dir")):
    global Engine, Session, Base

    def _fk_pragma_on_connect(dbapi_con, con_record):
        if use_mysql:
            return
        dbapi_con.execute("pragma foreign_keys=ON")

    if Engine is not None:
        raise Exception("Database engine already initialized")
    os.makedirs(db_directory, exist_ok=True)
    db_url = f"mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    Engine = create_engine(db_url, echo=False)
    event.listen(Engine, "connect", _fk_pragma_on_connect)
    Session = sessionmaker(bind=Engine)
    Base.metadata.bind = Engine


def get_courses_via_data_id(data_id_list: list[int]) -> list[Course]:
    course_list = []
    with Session.begin() as session:
        c_d_result = session.query(TBL_Course_Data).filter(TBL_Course_Data.course_data_id.in_(data_id_list)).all()
        for c_d_r in c_d_result:
            mt_result = session.query(TBL_Meeting).filter(TBL_Meeting.course_data_id == c_d_r.course_data_id).all()
            meeting_list = []
            for mt_r in mt_result:
                meeting_list.append(
                    Meeting(
                        time_start=mt_r.begin_time,
                        time_end=mt_r.end_time,
                        date_start=mt_r.start_date,
                        date_end=mt_r.end_date,
                        occurrence_unit=None,  # TODO: Temporary hardcode, needs to be calculated at scraper level.
                        occurrence_interval=None,  # TODO: Temporary hardcode, needs to be calculated at scraper level.
                        days_of_week=mt_r.days_of_week,
                        location=f"{mt_r.campus_description} {mt_r.building} {mt_r.room}",
                    )
                )
            c_fc_result = session.query(TBL_Course_Faculty.faculty_id).filter(
                TBL_Course_Faculty.course_data_id == c_d_r.course_data_id).all()
            faculty_list = []
            for c_fc_r in c_fc_result:
                fc_result = session.query(TBL_Faculty).filter(TBL_Faculty.faculty_id == c_fc_r.faculty_id).first()
                faculty_list.append(Instructor(faculty_id=fc_result.faculty_id, name=fc_result.instructor_name,
                                               email=fc_result.instructor_email, rating=fc_result.instructor_rating))
            course_list.append(
                Course(
                    course_code=session.query(TBL_Course).filter(
                        TBL_Course.course_id == c_d_r.course_id).first().course_code,
                    subject=c_d_r.subject,
                    subject_long=c_d_r.subject_long,
                    crn=c_d_r.crn,
                    class_type=(session.query(TBL_Class_Type.class_type).filter(
                        TBL_Class_Type.class_type_id == c_d_r.class_type_id).first()).class_type,
                    title=c_d_r.course_title,
                    section=c_d_r.sequence_number,
                    class_time=meeting_list,
                    is_linked=c_d_r.is_section_linked,
                    link_tag=c_d_r.link_identifier,
                    seats_filled=c_d_r.enrollment,
                    max_capacity=c_d_r.maximum_enrollment,
                    seats_available=c_d_r.seats_available,
                    is_virtual=True if "virtual" in c_d_r.instructional_method_description.lower() else False,
                    # TODO: This needs to be determined at scraper level ^.
                    restrictions=None,  # TODO: Temporary hardcode, needs restrictions support at scraper level.
                    instructional_method=c_d_r.instructional_method_description,
                    is_open=c_d_r.open_section,
                    wait_filled=c_d_r.wait_count,
                    wait_capacity=c_d_r.wait_capacity,
                    instructors=faculty_list
                )
            )
    return course_list
