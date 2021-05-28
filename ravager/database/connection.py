from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import os


class RavagerDB:
    def __init__(self):
        DATABASE_URL = os.environ.get("DATABASE_URL")
        engine = create_engine(DATABASE_URL, poolclass=NullPool)
        sql_session = sessionmaker(bind=engine)