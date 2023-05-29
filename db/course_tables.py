from sqlalchemy import (Column, Integer, Boolean, VARCHAR, ForeignKey)
from sqlalchemy import Date
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class TBL_Term(Base):
    __tablename__ = "tbl_term"

    term_id = Column(Integer, primary_key=True)
    term_description = Column(VARCHAR(128))


class TBL_Course(Base):
    __tablename__ = "tbl_course"

    course_id = Column(Integer, primary_key=True, autoincrement=True)
    term_id = Column(Integer, ForeignKey("tbl_term.term_id"))
    course_code = Column(VARCHAR(32))
    course_description = Column(VARCHAR(128))

    __table_args__ = (UniqueConstraint("term_id", "course_code", name="_term_id_course_code_constraint"),)


class TBL_Class_Type(Base):
    __tablename__ = "tbl_classtype"

    class_type_id = Column(Integer, primary_key=True, autoincrement=True)
    class_type = Column(VARCHAR(128))


class TBL_Course_Data(Base):
    __tablename__ = "tbl_course_data"

    course_data_id = Column(Integer, autoincrement=True, primary_key=True)
    course_id = Column(Integer, ForeignKey("tbl_course.course_id"))
    crn = Column(VARCHAR(32))
    sequence_number = Column(VARCHAR(128))
    id = Column(Integer)
    course_title = Column(VARCHAR(128))
    subject = Column(VARCHAR(128))
    subject_long = Column(VARCHAR(128))
    campus_description = Column(VARCHAR(128))
    class_type_id = Column(Integer, ForeignKey("tbl_classtype.class_type_id"))
    open_section = Column(Boolean)
    maximum_enrollment = Column(Integer)
    enrollment = Column(Integer)
    seats_available = Column(Integer)
    wait_capacity = Column(Integer)
    wait_count = Column(Integer)
    credit_hour_high = Column(Integer)
    credit_hour_low = Column(Integer)
    link_identifier = Column(VARCHAR(128))
    is_section_linked = Column(Boolean)
    instructional_method = Column(VARCHAR(128))
    instructional_method_description = Column(VARCHAR(128))

    __table_args__ = (UniqueConstraint("course_id", "crn", name="_course_id_crn_constraint"),)


class TBL_Course_Faculty(Base):
    __tablename__ = "tbl_course_faculty"

    course_data_id = Column(Integer, ForeignKey("tbl_course_data.course_data_id"), primary_key=True)
    faculty_id = Column(Integer, ForeignKey("tbl_faculty.faculty_id"), primary_key=True)


class TBL_Faculty(Base):
    __tablename__ = "tbl_faculty"

    faculty_id = Column(Integer, primary_key=True, autoincrement=True)
    instructor_name = Column(VARCHAR(128))
    instructor_email = Column(VARCHAR(128))
    instructor_rating = Column(Integer)


class TBL_Meeting(Base):
    __tablename__ = "tbl_meeting"

    meeting_id = Column(Integer, autoincrement=True, primary_key=True)
    course_data_id = Column(Integer, ForeignKey("tbl_course_data.course_data_id"))
    term_id = Column(Integer, ForeignKey("tbl_term.term_id"))
    crn = Column(VARCHAR(32))
    start_date = Column(Date)
    end_date = Column(Date)
    begin_time = Column(VARCHAR(128))
    end_time = Column(VARCHAR(128))
    days_of_week = Column(Integer)
    campus = Column(VARCHAR(128))
    campus_description = Column(VARCHAR(128))
    building = Column(VARCHAR(128))
    building_description = Column(VARCHAR(128))
    room = Column(VARCHAR(128))
    meeting_schedule_type = Column(VARCHAR(128))
