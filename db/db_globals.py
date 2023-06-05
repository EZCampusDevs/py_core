import os
from dotenv import load_dotenv

load_dotenv()

db_host = os.getenv("db_host")
db_port = os.getenv("db_port")
db_user = os.getenv("db_user")
db_pass = os.getenv("db_pass")
db_name = os.getenv("db_name")
db_dir = os.getenv("db_dir")


def check_env():
    if not db_dir:
        raise RuntimeError(
            "db_dir must be set! Set the environment variable or the value in db.db_globals"
        )
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
        raise RuntimeError(
            "db_name must be set! Set the environment variable or the value in db"
        )
