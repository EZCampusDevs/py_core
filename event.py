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
Event related DML abstraction.
"""

from datetime import date

from .classes.extended_meeting_class import ExtendedMeeting
from .db import SessionObj
from .db import db_globals as DG
from .db import db_tables as DT


def add_events(extended_meetings: list[ExtendedMeeting] | None = None):
    if extended_meetings is None or not extended_meetings:
        return

    session: SessionObj
    try:
        with DG.Session.begin() as session:
            for ex_mt in extended_meetings:
                session.add(
                    DT.TBL_Event(
                        timezone=ex_mt.timezone_str,
                        name=ex_mt.name,
                        description=ex_mt.description,
                        location=ex_mt.location,
                        seats_filled=ex_mt.seats_filled,
                        max_capacity=ex_mt.max_capacity,
                        color=ex_mt.colour,
                        is_virtual=ex_mt.is_virtual,
                        started_at=ex_mt.date_start,
                        ended_at=ex_mt.date_end,
                        begin_time=ex_mt.time_start,
                        end_time=ex_mt.time_end,
                        occurrence_unit=ex_mt.occurrence_unit,
                        occurrence_interval=ex_mt.occurrence_interval,
                        occurrence_repeat=(
                            ex_mt.occurrence_limit
                            if isinstance(ex_mt.occurrence_limit, int)
                            else None
                        ),
                        occurrence_until=(
                            ex_mt.occurrence_limit
                            if isinstance(ex_mt.occurrence_limit, date)
                            else None
                        ),
                        days_of_week=ex_mt.days_of_week,
                    )
                )

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


def get_events_via(event_ids: list[int] | None = None) -> list[ExtendedMeeting]:
    """Get a list of Course objects based on search parameters.

    Args:
        event_ids: Individual Course (CRN) data ids.
    Returns:
        List of Course objects based on search parameters.
    """
    if event_ids is None or not event_ids:
        return []

    session: SessionObj
    try:
        with DG.Session.begin() as session:
            result = session.query(DT.TBL_Event).filter(
                DT.TBL_Event.event_id.in_(event_ids),
            )
            return [
                ExtendedMeeting(
                    time_start=r.begin_time,
                    time_end=r.end_time,
                    date_start=r.started_at,
                    date_end=r.ended_at,
                    timezone_str=r.timezone,
                    occurrence_unit=r.occurrence_unit,
                    occurrence_interval=r.occurrence_interval,
                    occurrence_limit=(
                        r.occurrence_until
                        if isinstance(r.occurrence_until, date)
                        else r.occurrence_repeat  # int based limit.
                    ),
                    # TODO (py_core issue #13): The DB table structure allows for storage of both a
                    #  date (occurrence_until) and int (occurrence_repeat) based occurrence_limit.
                    #  On ExtendedMeeting initialization, a fair assumption must be decided in the
                    #  case both the date and int based limit is defined.
                    days_of_week=r.days_of_week,
                    location=r.location,
                    name=r.name,
                    description=r.description,
                    seats_filled=r.seats_filled,
                    max_capacity=r.max_capacity,
                    is_virtual=r.is_virtual,
                    colour=r.color,
                )
                for r in result
            ]
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
