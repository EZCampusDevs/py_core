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
User related DML abstraction.
"""

from sqlalchemy.orm.session import Session as SessionObj

from . import db_globals as DG
from .db_tables import TBL_User
from ..classes.user_classes import BasicUser


def get_users_via(usernames: list[str] | None = None) -> list[BasicUser]:
    """Get a list of Course objects based on search parameters.

    Args:
        usernames: List of individual usernames.

    Returns:
        List of BasicUser objects based on search parameters.
    """
    if usernames is None or not usernames:
        return []

    session: SessionObj
    try:
        with DG.Session.begin() as session:
            users = []
            users_result = session.query(TBL_User).filter(TBL_User.username.in_(usernames)).all()
            for result in users_result:
                users.append(
                    BasicUser(
                        username=result.username,
                        email=result.email,
                        hashed_password=result.password_hash,
                        name=result.display_name,
                        # description=,
                        # school_short_name=,
                        # program=,
                        # year_of_study=,
                        is_private=result.is_private,
                        is_suspended=result.is_suspended,
                        account_status=result.account_status,
                        # schedule_tag=,
                        created_at=result.created_at,
                        edited_at=result.edited_at,
                    )
                )
            return users
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


def add_users(users: list[BasicUser] | None = None):
    """Add BasicUsers to the database table.

    Args:
        users: List of BasicUsers.
    """
    if users is None or not users:
        return []

    db_users = []
    for user in users:
        db_users.append(
            TBL_User(
                username=user.username,
                email=user.email,
                password_hash=user.hashed_password,
                display_name=user.name,
                is_private=user.is_private,
                is_suspended=user.is_suspended,
                account_status=user.account_status,
            )
        )

    session: SessionObj
    try:
        with DG.Session.begin() as session:
            session.add_all(db_users)
            session.commit()
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
