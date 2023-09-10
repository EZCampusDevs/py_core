import logging

from sqlalchemy import (
    Date,
    DateTime,
    Float,
    Column,
    Index,
    Integer,
    Boolean,
    TIMESTAMP,
    BINARY,
    VARCHAR,
    ForeignKey,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func

from . import db_globals as DG


class TBL_Scrape_History(DG.Base):
    __tablename__ = "tbl_scrape_history"

    scrape_id = Column(Integer, primary_key=True, autoincrement=True)
    scrape_time = Column(TIMESTAMP)
    scrape_time_finished = Column(TIMESTAMP)
    has_finished_scraping = Column(Boolean)
    has_been_indexed = Column(Boolean)


class TBL_School(DG.Base):
    __tablename__ = "tbl_school"

    school_id = Column(Integer, primary_key=True)
    school_unique_value = Column(VARCHAR(128))
    subdomain = Column(VARCHAR(64))
    timezone = Column(VARCHAR(64))
    scrape_id_last = Column(Integer, ForeignKey(TBL_Scrape_History.scrape_id))


class TBL_Term(DG.Base):
    __tablename__ = "tbl_term"

    term_id = Column(Integer, primary_key=True, autoincrement=True)
    school_id = Column(Integer, ForeignKey(TBL_School.school_id))
    real_term_id = Column(Integer)
    term_description = Column(VARCHAR(128))

    __table_args__ = (
        UniqueConstraint("school_id", "real_term_id", name="_term_id_school_id_constraint"),
    )


class TBL_Course(DG.Base):
    __tablename__ = "tbl_course"

    course_id = Column(Integer, primary_key=True, autoincrement=True)
    term_id = Column(Integer, ForeignKey(TBL_Term.term_id))
    course_code = Column(VARCHAR(32))
    course_description = Column(VARCHAR(128))

    __table_args__ = (
        UniqueConstraint("term_id", "course_code", name="_term_id_course_code_constraint"),
    )


class TBL_Class_Type(DG.Base):
    __tablename__ = "tbl_classtype"

    class_type_id = Column(Integer, primary_key=True, autoincrement=True)
    class_type = Column(VARCHAR(128))


class TBL_Subject(DG.Base):
    __tablename__ = "tbl_subject"

    subject_id = Column(Integer, primary_key=True, autoincrement=True)
    # BIOL
    subject = Column(VARCHAR(128))
    # Biology
    subject_long = Column(VARCHAR(128))


class TBL_Course_Data(DG.Base):
    __tablename__ = "tbl_course_data"
    __table_args__ = (UniqueConstraint("course_id", "crn", name="_course_id_crn_constraint"),)

    # children1 = relationship("TBL_Meeting", backref='parent', passive_deletes=True)
    # children2 = relationship("TBL_Course_Faculty", backref='parent', passive_deletes=True)
    # children3 = relationship("TBL_Course_Restriction", backref='parent', passive_deletes=True)
    # children4 = relationship("TBL_Word_Course_Data", backref='parent', passive_deletes=True)

    course_data_id = Column(Integer, autoincrement=True, primary_key=True)

    course_id = Column(Integer, ForeignKey(TBL_Course.course_id))

    scrape_id = Column(Integer, ForeignKey(TBL_Scrape_History.scrape_id))

    class_type_id = Column(Integer, ForeignKey(TBL_Class_Type.class_type_id))

    subject_id = Column(Integer, ForeignKey(TBL_Subject.subject_id))

    # course reference number / crn
    crn = Column(VARCHAR(32))

    course_title = Column(VARCHAR(128))

    # which campus -> 'OT-North Oshawa'
    campus_description = Column(VARCHAR(128))

    maximum_enrollment = Column(Integer)
    current_enrollment = Column(Integer)

    maximum_waitlist = Column(Integer)
    current_waitlist = Column(Integer)

    credit_hours = Column(Integer)

    # this is actually instructionalMethodDescription
    delivery = Column(VARCHAR(128))

    open_section = Column(Boolean)
    link_identifier = Column(VARCHAR(128))
    is_section_linked = Column(Boolean)

    # 001 / 002 / 003...; conerting to int so will need to pad 0 later if needed
    sequence_number = Column(VARCHAR(128))

    should_be_indexed = Column(Boolean)
    

    def __repr__(self):

        return f"<CourseData {self.course_data_id} {self.course_id} {self.course_title}>"

class TBL_Faculty(DG.Base):
    __tablename__ = "tbl_faculty"

    faculty_id = Column(Integer, primary_key=True, autoincrement=True)
    banner_id = Column(BINARY(length=32), unique=True, nullable=False)
    scrape_id = Column(Integer, ForeignKey(TBL_Scrape_History.scrape_id))
    instructor_name = Column(VARCHAR(128))
    instructor_email = Column(VARCHAR(128))
    instructor_rating = Column(Integer)

class TBL_Course_Faculty(DG.Base):
    __tablename__ = "tbl_course_faculty"

    course_data_id = Column(Integer, ForeignKey(TBL_Course_Data.course_data_id, ondelete="CASCADE"), primary_key=True)
    parent = relationship(TBL_Course_Data, backref=backref('child_tbl_course_faculty', passive_deletes=True))

    faculty_id = Column(Integer, ForeignKey(TBL_Faculty.faculty_id), primary_key=True)

class TBL_Meeting(DG.Base):
    __tablename__ = "tbl_meeting"

    meeting_id = Column(Integer, autoincrement=True, primary_key=True)

    meeting_hash = Column(BINARY(length=32), unique=True, nullable=False)

    course_data_id = Column(Integer, ForeignKey(TBL_Course_Data.course_data_id, ondelete="CASCADE"))
    parent = relationship(TBL_Course_Data, backref=backref('child_tbl_course_meeting', passive_deletes=True))

    scrape_id = Column(Integer, ForeignKey(TBL_Scrape_History.scrape_id))

    term_id = Column(Integer, ForeignKey(TBL_Term.term_id))

    crn = Column(VARCHAR(32))

    building = Column(VARCHAR(128))
    building_description = Column(VARCHAR(128))

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

    restriction_type = Column(Integer, ForeignKey(TBL_Restriction_Type.restriction_type_id))


class TBL_Course_Restriction(DG.Base):
    __tablename__ = "tbl_course_restriction"

    course_data_id = Column(Integer, ForeignKey(TBL_Course_Data.course_data_id, ondelete="CASCADE"), primary_key=True)
    parent = relationship(TBL_Course_Data, backref=backref('child_tbl_course_restriction', passive_deletes=True))
    restriction_id = Column(Integer, ForeignKey(TBL_Restriction.restriction_id), primary_key=True)


class TBL_Word(DG.Base):
    __tablename__ = "tbl_word"

    word_id = Column(Integer, primary_key=True)
    word = Column(VARCHAR(255), unique=True)

    __table_args__ = (Index("word_index", "word"),)


class TBL_Word_Course_Data(DG.Base):
    __tablename__ = "tbl_word_course_data"

    word_id = Column(Integer, ForeignKey(TBL_Word.word_id), primary_key=True)
    course_data_id = Column(Integer, ForeignKey(TBL_Course_Data.course_data_id, ondelete="CASCADE"), primary_key=True)
    parent = relationship(TBL_Course_Data, backref=backref('child_tbl_word_course_data', passive_deletes=True))
    count = Column(Integer)


class TBL_Report_Type(DG.Base):
    __tablename__ = "tbl_report_type"
    report_type_id = Column(Integer, primary_key=True, autoincrement=True)
    report_type_name = Column(VARCHAR(128))
    report_type_description = Column(VARCHAR(512))


class TBL_Operating_System(DG.Base):
    __tablename__ = "tbl_operating_system"
    os_id = Column(Integer, primary_key=True, autoincrement=True)
    os_name = Column(VARCHAR(128))


class TBL_Browser(DG.Base):
    __tablename__ = "tbl_browser"
    browser_id = Column(Integer, primary_key=True, autoincrement=True)
    browser_name = Column(VARCHAR(128))
    browser_version = Column(VARCHAR(128))


class TBL_Report(DG.Base):
    __tablename__ = "tbl_report"

    report_id = Column(Integer, primary_key=True, autoincrement=True)
    report_type = Column(Integer, ForeignKey(TBL_Report_Type.report_type_id))
    operating_system = Column(Integer, ForeignKey(TBL_Operating_System.os_id))
    browser_description = Column(Integer, ForeignKey(TBL_Browser.browser_id))
    created_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    description = Column(Text)




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
        TBL_Subject.__tablename__,
        TBL_Browser.__tablename__,
        TBL_Operating_System.__tablename__,
        TBL_Report_Type.__tablename__,
        TBL_Report.__tablename__,
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
