import os

from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker, declarative_base

Engine = None
Session: sessionmaker = None
Base = declarative_base()

Database_Initialized = False

load_dotenv()

db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
db_dir = os.getenv("DB_DIR")


def check_env():
    if not db_host:
        raise RuntimeError(
            "db_host must be set! Set the environment variable or the value in db.db_globals"
        )
    if not db_port:
        raise RuntimeError(
            "db_port must be set! Set the environment variable or the value in db.db_globals"
        )
    if not db_user:
        raise RuntimeError(
            "db_user must be set! Set the environment variable or the value in db.db_globals"
        )
    if not db_pass:
        raise RuntimeError(
            "db_pass must be set! Set the environment variable or the value in db.db_globals"
        )
    if not db_name:
        raise RuntimeError("db_name must be set! Set the environment variable or the value in db")
