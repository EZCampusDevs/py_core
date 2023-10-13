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
from . import db, classes, logging_util, user


def init_drop_create_db():
    logging_util.setup_logging()
    db.init_database(
        db_host="localhost",
        db_port=3306,
        db_user="test",
        db_pass="root",
        db_name="hibernate_db",
        load_env=False,
    )
    # db.DT.drop_all()
    # db.DT.create_all()

def test_usersa():

    session: db.SessionObj

    with db.Session().begin() as session:
        
        username = "test"
        password = "password"
        hashed = classes.user_classes.hash_password(password)
        
        logging.debug(f"{type(hashed)} {hashed}")

        user.insert_user_nt(session, username,email="",password=hashed)
        
        for i in user.select_users_by_name_nt(session, username):

            logging.info(f"{i.user_id} {i.username} {i.password_hash}")

            logging.info(f"Password matches: {classes.user_classes.verify_password(password, i.password_hash)}") 

def test_usersb():

    session: db.SessionObj

    with db.Session().begin() as session:
        
        username = "testa"
        password = "passwordalsdkjasldkjas"
        users = [
            classes.user_classes.BasicUser(
                username=username,
                email="test@gmail.com",
                password=password,
                name="test",
                description="some random user for testing",
                is_private=False,
                is_suspended=False,
                account_status=0,
                created_at=0,
                edited_at=0,
            )
        ]

        user.add_users(users)
        
        for i in user.select_users_by_name_nt(session, username):

            logging.info(f"{i.user_id} {i.username} {i.password_hash}")

            logging.info(f"Password matches: {classes.user_classes.verify_password(password, i.password_hash)}") 

def main():

    init_drop_create_db()

    test_usersa()

    test_usersb()