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

from . import SessionObj
from . import Session
from . import db_globals as DG
from . import db_tables as DT


def insert_user_nt(session: SessionObj, username: str, email:str, password: bytes, is_suspended: bool = False) -> None:
    
    logging.debug(f"Inserting user with name {username} and password with length {len(password)}")

    usr = DT.TBL_User()
    usr.username = username
    usr.email = email
    usr.password_hash = password
    usr.is_suspended = is_suspended
    usr.account_status = 0
    
    session.add(usr)
    

def insert_user(session: SessionObj, username: str, email:str, password: bytes, is_suspended: bool = False) -> None:
    
    with Session().begin() as session:

        insert_user_nt(session, username, email, password, is_suspended)
    

def select_users_by_name_nt(session: SessionObj, username: str) -> list[DT.TBL_User]:
    
    logging.debug(f"Selecting users with name {username}")
    
    return session.query(DT.TBL_User).filter_by(username = username).all()
