from celery import uuid
from ravager.database.helpers.structs import UserStruct
from ravager.database.users import UserData
from ravager.database.tasks import Tasks
import json
from ravager.services.google.upload import Upload


def upload_file(task, message):
    celery_task_id = uuid()
    task.msg_id = message.message_id

    file_path = task.file_path
    aria_folder_id = str(file_path.split("/")[-1])
    user = UserStruct()
    user.user_id = task.user_id
    user = UserData(user=user).get_user()
    if user.storage_type == "personal":
        google_directory = "personal"
    elif user.storage_type == "shared":
        google_directory = str(user.drive_id)
    if task.status == "uploaded" or task.status == "downloaded":
        task.drive_id_dict = json.dumps({aria_folder_id: [google_directory], "used_drive_ids": {}})
        task.uploaded_files = None

    task.task_id = celery_task_id
    Tasks(task=task).set_task()
    task = task.to_json()
    Upload().upload.apply_async(kwargs={"task": task}, task_id=celery_task_id)
