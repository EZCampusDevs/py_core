import os

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

# It's very important you don't import Engine, Session, and Base directly because the get modified
#  at runtime, so you should use the functions below to access them.
from . import db_globals as DG
from . import db_tables as DT


def Session():
    return DG.Session


def Engine():
    return DG.Engine


def Base():
    return DG.Base


def init_database(
    use_mysql: bool = True,
    db_host: str = DG.db_host,
    db_port: str = DG.db_port,
    db_name: str = DG.db_name,
    db_user: str = DG.db_user,
    db_pass: str = DG.db_pass,
    db_directory: str = DG.db_dir,
    create: bool = True,
    check_env: bool = True,
):
    if DG.Database_Initialized:
        raise Exception("Database engine already initialized")

    if check_env:
        DG.check_env()

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
        DT.create_all()

    DG.Database_Initialized = True
