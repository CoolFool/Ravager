from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Optional


@dataclass_json
@dataclass
class UserStruct:
    id: Optional[int] = None
    user_id: Optional[str] = None
    state: Optional[str] = None
    refresh_token: Optional[str] = None
    storage_type: Optional[str] = None
    drive_id: Optional[str] = None
    authorized: Optional[bool] = None
    tg_username: Optional[str] = None
    tg_firstname: Optional[str] = None
    tg_group_title: Optional[str] = None
    tg_group_admins: Optional[any] = None
    stats: Optional[any] = None
    blocked: Optional[bool] = None
    is_admin: Optional[bool] = None
    email: Optional[str] = None


@dataclass_json
@dataclass
class OpsDataStruct:
    id: Optional[int] = None
    task_id: Optional[str] = None
    file_id: Optional[str] = None
    gid: Optional[str] = None
    user_id: Optional[str] = None
    drive_id_dict: Optional[str] = None
    status: Optional[str] = None
    file_path: Optional[str] = None
    start_time_stamp: Optional[str] = None
    end_time_stamp: Optional[str] = None
    msg_id: Optional[str] = None
    source_msg_id: Optional[str] = None
    uploaded_files: Optional[str] = None
