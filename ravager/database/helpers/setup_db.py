from sqlalchemy import Column, String, Boolean, JSON, Integer
from sqlalchemy.types import PickleType
from sqlalchemy.ext.mutable import MutableList, MutableDict
from sqlalchemy.ext.declarative import declarative_base
from ravager.database import engine

Base = declarative_base()


class User(Base):
    __tablename__ = "user_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String)
    state = Column(String)
    refresh_token = Column(String)
    storage_type = Column(String)
    drive_id = Column(String)
    authorized = Column(Boolean)
    tg_username = Column(String)
    tg_firstname = Column(String)
    tg_group_title = Column(String)
    email = Column(String)
    tg_group_admins = Column(MutableList.as_mutable(PickleType),
                             default=[])
    blocked = Column(Boolean)
    is_admin = Column(Boolean)
    stats = Column(JSON)


class Task(Base):
    __tablename__ = "operation_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String)
    file_id = Column(String)
    gid = Column(String)
    user_id = Column(String)
    drive_id_dict = Column(String)
    status = Column(String)
    file_path = Column(String)
    start_time_stamp = Column(String)
    end_time_stamp = Column(String)
    msg_id = Column(String)
    source_msg_id = Column(String)
    uploaded_files = Column(String)


def create_tables():
    try:
        Base.metadata.create_all(engine)
    except Exception as e:
        logger.error(e)
        raise SystemError("Fatal error during tables creation")
