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

import logging

from . db import Session, SessionObj
from . db import db_globals as DG
from . db import db_tables as DT

from . classes.user_classes import BasicUser


def insert_user_nt(session: SessionObj, username: str, email:str, password: bytes, is_suspended: bool = False) -> None:
    
    logging.debug(f"Inserting user with name {username} and password with length {len(password)}")

    usr = DT.TBL_User()
    usr.username = username
    usr.email = email
    usr.password_hash = password
    usr.is_suspended = is_suspended
    usr.account_status = 0
    usr.is_private = 1
    
    session.add(usr)
    

def insert_user(session: SessionObj, username: str, email:str, password: bytes, is_suspended: bool = False) -> None:
    
    with Session().begin() as session:

        insert_user_nt(session, username, email, password, is_suspended)
    

def select_users_by_name_nt(session: SessionObj, username: str) -> list[DT.TBL_User]:
    
    logging.debug(f"Selecting users with name {username}")
    
    return session.query(DT.TBL_User).filter_by(username = username).all()


def get_users_via(usernames: list[str] | None = None) -> list[BasicUser]:
    """Get a list of Course objects based on search parameters.

    Args:
        usernames: List of individual usernames.

    Returns:
        List of BasicUser objects based on search parameters.
    """
    if usernames is None or not usernames:
        return []

    try:

        session: SessionObj
        with Session().begin() as session:

            users_result = session.query(DT.TBL_User).filter(DT.TBL_User.username.in_(usernames)).all()
            
            return [
                    BasicUser(
                        username=result.username,
                        email=result.email,
                        password=result.password_hash,
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
                    )
            for result in users_result
            ]
        
    except AttributeError as e:

        msg = e.args[0]

        if "'NoneType' object has no attribute 'begin'" in msg:

            raise RuntimeWarning(
                f"{msg} <--- Daniel: Check (local / ssh) connection to DB, possible missing "
                f"init_database() call via 'from py_core.db import init_database'"
            )

        raise e


def add_users(users: list[BasicUser] | None = None):
    """Add BasicUsers to the database table.

    Args:
        users: List of BasicUsers.
    """

    if users is None or not users:
        return []

    try:

        session: SessionObj

        with Session().begin() as session:

            for user in users:
                
                u = DT.TBL_User(
                    username=user.username,
                    email=user.email,
                    password_hash=user.get_hashed_password(),
                    display_name=user.name,
                    is_private=user.is_private,
                    is_suspended=user.is_suspended,
                    account_status=user.account_status,
                )
                
                session.add(u)

    except AttributeError as e:

        msg = e.args[0]

        if "'NoneType' object has no attribute 'begin'" in msg:
            raise RuntimeWarning(
                f"{msg} <--- Daniel: Check (local / ssh) connection to DB, possible missing "
                f"init_database() call via 'from py_core.db import init_database'"
            )

        raise e
