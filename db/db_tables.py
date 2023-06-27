import logging

from sqlalchemy import (
    Date,
    Float,
    Column,
    Index,
    Integer,
    Boolean,
    TIMESTAMP,
    BINARY,
    VARCHAR,
    ForeignKey,
    String,
    Table,
)
from sqlalchemy import UniqueConstraint

from . import db_globals as DG


class TBL_Scrape_History(DG.Base):
    __tablename__ = "tbl_scrape_history"

    scrape_id = Column(Integer, primary_key=True, autoincrement=True)
    scrape_time = Column(TIMESTAMP)
    has_been_indexed = Column(Boolean)


class TBL_School(DG.Base):
    __tablename__ = "tbl_school"

    school_id = Column(Integer, primary_key=True)
    school_unique_value = Column(VARCHAR(128))
    subdomain = Column(VARCHAR(64))


class TBL_Term(DG.Base):
    __tablename__ = "tbl_term"

    term_id = Column(Integer, primary_key=True, autoincrement=True)
    school_id = Column(Integer, ForeignKey("tbl_school.school_id"))
    real_term_id = Column(Integer)
    term_description = Column(VARCHAR(128))

    __table_args__ = (
        UniqueConstraint("school_id", "real_term_id", name="_term_id_school_id_constraint"),
    )


class TBL_Course(DG.Base):
    __tablename__ = "tbl_course"

    course_id = Column(Integer, primary_key=True, autoincrement=True)
    term_id = Column(Integer, ForeignKey("tbl_term.term_id"))
    course_code = Column(VARCHAR(32))
    course_description = Column(VARCHAR(128))

    __table_args__ = (
        UniqueConstraint("term_id", "course_code", name="_term_id_course_code_constraint"),
    )


class TBL_Class_Type(DG.Base):
    __tablename__ = "tbl_classtype"

    class_type_id = Column(Integer, primary_key=True, autoincrement=True)
    class_type = Column(VARCHAR(128))


class TBL_Course_Data(DG.Base):
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
    # cross_list = Column(VARCHAR)
    # cross_list_capacity = Column(VARCHAR)
    # cross_list_count = Column(Integer)
    # cross_list_available = Column(Integer)
    credit_hour_high = Column(Integer)
    credit_hour_low = Column(Integer)
    # credit_hour_indicator = Column(VARCHAR)
    open_section = Column(Boolean)
    link_identifier = Column(VARCHAR(128))
    is_section_linked = Column(Boolean)
    # reserved_seat_summary = Column(VARCHAR)
    # section_attributes = Column(VARCHAR)

    # CLS -> In-Person
    # WB1 -> Virtual Meet Times
    instructional_method = Column(VARCHAR(128))

    # In-Person
    # Virtual Meet Times
    instructional_method_description = Column(VARCHAR(128))

    __table_args__ = (UniqueConstraint("course_id", "crn", name="_course_id_crn_constraint"),)


class TBL_Course_Faculty(DG.Base):
    __tablename__ = "tbl_course_faculty"

    course_data_id = Column(Integer, ForeignKey("tbl_course_data.course_data_id"), primary_key=True)

    faculty_id = Column(Integer, ForeignKey("tbl_faculty.faculty_id"), primary_key=True)


class TBL_Faculty(DG.Base):
    __tablename__ = "tbl_faculty"

    faculty_id = Column(Integer, primary_key=True, autoincrement=True)
    banner_id = Column(BINARY(length=32), unique=True, nullable=False)
    scrape_id = Column(Integer, ForeignKey("tbl_scrape_history.scrape_id"))
    instructor_name = Column(VARCHAR(128))
    instructor_email = Column(VARCHAR(128))
    instructor_rating = Column(Integer)


class TBL_Meeting(DG.Base):
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


class TBL_Restriction_Type(DG.Base):
    __tablename__ = "tbl_restriction_type"

    restriction_type_id = Column(Integer, primary_key=True, autoincrement=True)
    restriction_type = Column(VARCHAR(128))


class TBL_Restriction(DG.Base):
    __tablename__ = "tbl_restriction"

    restriction_id = Column(Integer, primary_key=True, autoincrement=True)
    restriction = Column(VARCHAR(128))
    must_be_in = Column(Boolean)

    restriction_type = Column(Integer, ForeignKey("tbl_restriction_type.restriction_type_id"))


class TBL_Course_Restriction(DG.Base):
    __tablename__ = "tbl_course_restriction"

    course_data_id = Column(Integer, ForeignKey("tbl_course_data.course_data_id"), primary_key=True)
    restriction_id = Column(Integer, ForeignKey("tbl_restriction.restriction_id"), primary_key=True)

class TBL_Word(DG.Base):
    __tablename__ = 'tbl_word'
    
    word_id = Column(Integer, primary_key=True)
    word = Column(VARCHAR(255), unique=True)
    
    __table_args__ = (
        Index('word_index', 'word'),
    )


class TBL_Word_Course_Data(DG.Base):
    __tablename__ = 'tbl_word_course_data'

    word_id = Column(Integer, ForeignKey('tbl_word.word_id'), primary_key=True)
    course_data_id = Column(Integer, ForeignKey('tbl_course_data.course_data_id'), primary_key=True)
    count = Column(Integer)


def create_all():
    DG.Base.metadata.create_all(DG.Engine)


def drop_all():
    db_names = [
        TBL_Faculty.__tablename__,
        TBL_Class_Type.__tablename__,
        TBL_Course.__tablename__,
        TBL_Course_Data.__tablename__,
        TBL_Course_Faculty.__tablename__,
        TBL_Scrape_History.__tablename__,
        TBL_Meeting.__tablename__,
        TBL_Term.__tablename__,
        TBL_Course_Restriction.__tablename__,
        TBL_Restriction.__tablename__,
        TBL_Restriction_Type.__tablename__,
        TBL_School.__tablename__,
        TBL_Word.__tablename__,
        TBL_Word_Course_Data.__tablename__,
    ]
    for name in db_names:
        for name in db_names:
            try:
                table = Table(name, DG.Base.metadata)
                table.drop(DG.Engine)
            except Exception as e:
                if "referenced by a foreign key constraint" in str(e):
                    continue
                if "Unknown table" in str(e):
                    continue
                logging.warn(e)
