from sqlalchemy.orm import sessionmaker, declarative_base

Engine = None
Session: sessionmaker = None
Base = declarative_base()

Database_Initialized = False
