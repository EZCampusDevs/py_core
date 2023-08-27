import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import sessionmaker

# It's very important you don't import Engine, Session, and Base directly because the get modified
#  at runtime, so you should use the functions below to access them.
from . import db_globals as DG
from . import db_tables as DT

load_dotenv()

def Session():
    return DG.Session

def Engine():
    return DG.Engine

def Base():
    return DG.Base

def get_env_db_host(default=None):
    return os.getenv("DB_HOST", default)

def get_env_db_port(default=None):
    return os.getenv("DB_PORT", default)

def get_env_db_user(default=None):
    return os.getenv("DB_USER", default)

def get_env_db_password(default=None):
    return os.getenv("DB_PASSWORD", default)

def get_env_db_name(default=None):
    return os.getenv("DB_NAME", default)

def get_env_db_dir(default=None):
    return os.getenv("DB_DIR", default)


def check_env():
    if not get_env_db_host():
        raise RuntimeError(
            "db_host must be set! Set the environment variable or the value in db.db_globals"
        )
    if not get_env_db_port():
        raise RuntimeError(
            "db_port must be set! Set the environment variable or the value in db.db_globals"
        )
    if not get_env_db_user():
        raise RuntimeError(
            "db_user must be set! Set the environment variable or the value in db.db_globals"
        )
    if not get_env_db_password():
        raise RuntimeError(
            "db_pass must be set! Set the environment variable or the value in db.db_globals"
        )
    if not get_env_db_name():
        raise RuntimeError("db_name must be set! Set the environment variable or the value in db")


def init_database(
    use_mysql: bool = True,
    db_host: str = get_env_db_host(),
    db_port: str = get_env_db_port(),
    db_name: str = get_env_db_name(),
    db_user: str = get_env_db_user(),
    db_pass: str = get_env_db_password(),
    db_directory: str = get_env_db_dir(),
    create: bool = True,
    check_env: bool = True,
):
    if DG.Database_Initialized:
        raise Exception("Database engine already initialized")

    if check_env:
        check_env()

    if db_directory:
        os.makedirs(db_directory, exist_ok=True)

    db_url = f"mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    DG.Engine = create_engine(db_url, echo=False)

    if not use_mysql:

        def _fk_pragma_on_connect(dbapi_con, con_record):
            dbapi_con.execute("pragma foreign_keys=ON")

        event.listen(DG.Engine, "connect", _fk_pragma_on_connect)

    DG.Session = sessionmaker(bind=DG.Engine)
    DG.Base.metadata.bind = DG.Engine

    if create:
        try:
            DT.create_all()
        except DatabaseError as e:
            msg = e.args[0]
            if "Can't connect to MySQL server on" in msg:
                raise RuntimeWarning(f"{msg} <--- Daniel: Check (local / ssh) connection to DB")
            else:
                raise e

    DG.Database_Initialized = True
