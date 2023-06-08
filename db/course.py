# TODO: Tables should probably get some column name standardization fix.

import os
from datetime import datetime

from sqlalchemy import (
    and_,
    not_,
    or_,
    create_engine,
    event,
    Column,
    BINARY,
    Float,
    Integer,
    Boolean,
    VARCHAR,
    TIMESTAMP,
    ForeignKey,
    Date,
    UniqueConstraint,
)
from sqlalchemy.orm import sessionmaker, declarative_base

from ..classes.course_class import Course, merge_course_meeting_occurrences
from ..classes.instructor_class import Instructor
from ..classes.meeting_class import Meeting

from . import db_globals as DG

Engine = None
Session: sessionmaker = None
Base = declarative_base()


def init_database(
    use_mysql: bool = True,
    db_host: str = DG.db_host,
    db_port: str = DG.db_port,
    db_name: str = DG.db_name,
    db_user: str = DG.db_user,
    db_pass: str = DG.db_pass,
    db_directory: str = DG.db_dir,
):
    global Engine, Session, Base

    DG.check_env()

    def _fk_pragma_on_connect(dbapi_con, con_record):
        if use_mysql:
            return
        dbapi_con.execute("pragma foreign_keys=ON")

    if Engine is not None:
        raise Exception("Database engine already initialized")

    if db_directory:
        os.makedirs(db_directory, exist_ok=True)

    db_url = f"mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    Engine = create_engine(db_url, echo=False)
    event.listen(Engine, "connect", _fk_pragma_on_connect)
    Session = sessionmaker(bind=Engine)
    Base.metadata.bind = Engine


init_database()  # TODO: Fix this to be prod ready, for quick testing purposes only!!!


class TBL_Scrape_History(Base):
    __tablename__ = "tbl_scrape_history"

    scrape_id = Column(Integer, primary_key=True, autoincrement=True)
    scrape_time = Column(TIMESTAMP)
    has_been_indexed = Column(Boolean)


class TBL_School(Base):
    __tablename__ = "tbl_school"

    school_id = Column(Integer, primary_key=True)
    school_unique_value = Column(VARCHAR(128))


class TBL_Term(Base):
    __tablename__ = "tbl_term"

    term_id = Column(Integer, primary_key=True)
    school_id = Column(Integer, ForeignKey("tbl_school.school_id"), primary_key=True)
    term_description = Column(VARCHAR(128))


class TBL_Course(Base):
    __tablename__ = "tbl_course"

    course_id = Column(Integer, primary_key=True, autoincrement=True)
    term_id = Column(Integer, ForeignKey("tbl_term.term_id"), primary_key=True)
    course_code = Column(VARCHAR(32))
    course_description = Column(VARCHAR(128))


class TBL_Class_Type(Base):
    __tablename__ = "tbl_classtype"

    class_type_id = Column(Integer, primary_key=True, autoincrement=True)
    class_type = Column(VARCHAR(128))


class TBL_Course_Data(Base):
    __tablename__ = "tbl_course_data"

    course_data_id = Column(Integer, autoincrement=True, primary_key=True)

    course_id = Column(Integer, ForeignKey("tbl_course.course_id"))

    scrape_id = Column(Integer, ForeignKey("tbl_scrape_history.scrape_id"))

    # course reference number / crn
    crn = Column(VARCHAR(32))
    # i'm not really sure what this actually is
    id = Column(Integer)

    # Biology II
    course_title = Column(VARCHAR(128))
    # BIOL
    subject = Column(VARCHAR(128))
    # Biology
    subject_long = Column(VARCHAR(128))

    # 001 / 002 / 003...; conerting to int so will need to pad 0 later if needed
    sequence_number = Column(VARCHAR(128))

    # which campus -> 'OT-North Oshawa'
    campus_description = Column(VARCHAR(128))

    # lab, lecture, tutorial
    class_type_id = Column(Integer, ForeignKey("tbl_classtype.class_type_id"))

    credit_hours = Column(Integer)
    maximum_enrollment = Column(Integer)
    enrollment = Column(Integer)
    seats_available = Column(Integer)
    wait_capacity = Column(Integer)
    wait_count = Column(Integer)
    wait_available = Column(Integer)
    credit_hour_high = Column(Integer)
    credit_hour_low = Column(Integer)
    open_section = Column(Boolean)
    link_identifier = Column(VARCHAR(128))
    is_section_linked = Column(Boolean)

    # CLS -> In-Person
    # WB1 -> Virtual Meet Times
    instructional_method = Column(VARCHAR(128))

    # In-Person
    # Virtual Meet Times
    instructional_method_description = Column(VARCHAR(128))

    __table_args__ = (
        UniqueConstraint("course_id", "crn", name="_course_id_crn_constraint"),
    )


class TBL_Course_Faculty(Base):
    __tablename__ = "tbl_course_faculty"

    course_data_id = Column(
        Integer, ForeignKey("tbl_course_data.course_data_id"), primary_key=True
    )

    faculty_id = Column(Integer, ForeignKey("tbl_faculty.faculty_id"), primary_key=True)


class TBL_Faculty(Base):
    __tablename__ = "tbl_faculty"

    faculty_id = Column(Integer, primary_key=True, autoincrement=True)
    banner_id = Column(BINARY(length=32), unique=True, nullable=False)
    scrape_id = Column(Integer, ForeignKey("tbl_scrape_history.scrape_id"))
    instructor_name = Column(VARCHAR(128))
    instructor_email = Column(VARCHAR(128))
    instructor_rating = Column(Integer)


class TBL_Meeting(Base):
    __tablename__ = "tbl_meeting"

    meeting_id = Column(Integer, autoincrement=True, primary_key=True)

    meeting_hash = Column(BINARY(length=32), unique=True, nullable=False)

    course_data_id = Column(Integer, ForeignKey("tbl_course_data.course_data_id"))

    term_id = Column(Integer, ForeignKey("tbl_term.term_id"))

    crn = Column(VARCHAR(32))

    building = Column(VARCHAR(128))
    building_description = Column(VARCHAR(128))

    campus = Column(VARCHAR(128))
    campus_description = Column(VARCHAR(128))

    meeting_type = Column(VARCHAR(128))
    meeting_type_description = Column(VARCHAR(128))

    start_date = Column(Date)
    end_date = Column(Date)

    begin_time = Column(VARCHAR(128))
    end_time = Column(VARCHAR(128))

    time_delta = Column(Integer)

    days_of_week = Column(Integer)

    room = Column(VARCHAR(128))

    category = Column(VARCHAR(128))
    credit_hour_session = Column(Float)
    hours_week = Column(Float)
    meeting_schedule_type = Column(VARCHAR(128))


class TBL_Restriction_Type(Base):
    __tablename__ = "tbl_restriction_type"

    restriction_type_id = Column(Integer, primary_key=True, autoincrement=True)
    restriction_type = Column(VARCHAR(128))


class TBL_Restriction(Base):
    __tablename__ = "tbl_restriction"

    restriction_id = Column(Integer, primary_key=True, autoincrement=True)
    restriction = Column(VARCHAR(128))
    must_be_in = Column(Boolean)

    restriction_type = Column(
        Integer, ForeignKey("tbl_restriction_type.restriction_type_id")
    )


class TBL_Course_Restriction(Base):
    __tablename__ = "tbl_course_restriction"

    course_data_id = Column(
        Integer, ForeignKey("tbl_course_data.course_data_id"), primary_key=True
    )
    restriction_id = Column(
        Integer, ForeignKey("tbl_restriction.restriction_id"), primary_key=True
    )


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
    with Session.begin() as session:
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
                            time_start=datetime.strptime(
                                str(mt_r.begin_time), "%H%M"
                            ).time(),
                            time_end=datetime.strptime(
                                str(mt_r.end_time), "%H%M"
                            ).time(),
                            date_start=mt_r.start_date,
                            date_end=mt_r.end_date,
                            occurrence_unit=None,
                            # TODO: Temporary hardcode, needs to be calculated at scraper level.
                            occurrence_interval=None,
                            # TODO: Temporary hardcode, needs to be calculated at scraper level.
                            occurrence_limit=None,
                            # TODO: Temporary hardcode, needs to be calculated at scraper level.
                            days_of_week=mt_r.days_of_week,
                            location=f"{mt_r.campus_description} {mt_r.building} {mt_r.room}",
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
                    subject=c_d_r.subject,
                    subject_long=c_d_r.subject_long,
                    crn=c_d_r.crn,
                    class_type=(
                        session.query(TBL_Class_Type.class_type)
                        .filter(TBL_Class_Type.class_type_id == c_d_r.class_type_id)
                        .first()
                    ).class_type,
                    title=c_d_r.course_title,
                    section=c_d_r.sequence_number,
                    class_time=meeting_list,
                    is_linked=c_d_r.is_section_linked,
                    link_tag=c_d_r.link_identifier,
                    seats_filled=c_d_r.enrollment,
                    max_capacity=c_d_r.maximum_enrollment,
                    seats_available=c_d_r.seats_available,
                    is_virtual=True
                    if "virtual" in c_d_r.instructional_method_description.lower()
                    else False,
                    # TODO: This needs to be determined at scraper level ^.
                    restrictions=None,
                    # TODO: Temporary hardcode, needs restrictions support at scraper level.
                    instructional_method=c_d_r.instructional_method_description,
                    is_open=c_d_r.open_section,
                    wait_filled=c_d_r.wait_count,
                    wait_capacity=c_d_r.wait_capacity,
                    instructors=faculty_list,
                )
            )
    return [merge_course_meeting_occurrences(c) for c in course_list]
