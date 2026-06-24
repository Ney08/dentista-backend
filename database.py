from sqlalchemy import create_engine
from sqlalchemy import event

from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv

import os


"""
==========================================
LOAD ENV
==========================================
"""

load_dotenv()


"""
==========================================
DATABASE URL
==========================================
"""

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./dentista.db"
)


"""
==========================================
ENGINE CONFIG
==========================================
"""

connect_args = {}

if DATABASE_URL.startswith("sqlite"):

    connect_args = {
        "check_same_thread": False
    }


"""
==========================================
ENGINE
==========================================
"""

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
)


"""
==========================================
SQLITE FOREIGN KEYS
==========================================
"""

if DATABASE_URL.startswith("sqlite"):

    @event.listens_for(
        engine,
        "connect"
    )
    def set_sqlite_pragma(
        dbapi_connection,
        connection_record
    ):

        cursor = dbapi_connection.cursor()

        cursor.execute(
            "PRAGMA foreign_keys=ON"
        )

        cursor.close()


"""
==========================================
SESSION
==========================================
"""

SessionLocal = sessionmaker(

    autocommit=False,

    autoflush=False,

    bind=engine

)


"""
==========================================
BASE
==========================================
"""

Base = declarative_base()


"""
==========================================
GET DB
==========================================
"""

def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()