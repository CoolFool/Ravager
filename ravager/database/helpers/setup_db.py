from sqlalchemy import Column, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from ravager.database import engine, session, sessionmaker
from sqlalchemy import exc

import json

Base = declarative_base()

admin_config = json.dumps(
        {
            "admin_options": {
                "admins": [],
                "allow_admin_setup": False
            },
            "limits": {
                "max_tasks_per_chat": 2,
                "abort_cooldown": 30,
                "max_concurrent_downloads": 3,
                "max_concurrent_uploads": 3
            },
            "filter_config": {
                "whitelist_enabled": True,
                "group_whitelist_password": "",
                "private_whitelist_password": ""
            },
            "first_setup": True
        })

filter_config = json.dumps({
    "allowed_users": [],
    "blocked_users": []
})


class User(Base):
    __tablename__ = "user_data"

    user_id = Column(String, primary_key=True)
    state = Column(String)
    refresh_token = Column(String)
    storage_type = Column(String)
    drive_id = Column(String)
    authorized = Column(Boolean)
    tg_username = Column(String)
    stats = Column(String)
    blocked = Column(Boolean)


class Operation(Base):
    __tablename__ = "operation_data"

    task_id = Column(String, primary_key=True)
    user_id = Column(String)
    returned_task_data = Column(String)
    upload_data = Column(String)
    google_drive_id_dict = Column(String)
    status = Column(String)
    file_path = Column(String)
    start_time_stamp = Column(String)
    end_time_stamp = Column(String)


class Admin(Base):
    __tablename__ = "admin_data"

    user_id = Column(String, primary_key=True)
    filter = Column(String)
    admin_config = Column(String)


def create_tables():
    try:
        Base.metadata.create_all(engine)
        return True
    except Exception as e:
        print(e)
        raise SystemError("Fatal error during tables creation")


def insert_default_admin_conf():
    try:
        set_admin_row = Admin(user_id="admin", admin_config=admin_config, filter=filter_config)
        session.add(set_admin_row)
        session.commit()
    except exc.IntegrityError:
        print("Admin defaults already configured")
    finally:
        sessionmaker.close_all()
