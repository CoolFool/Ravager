import time

from ravager.database.users import UserData
from ravager.database.tasks import Tasks
import os
import json
from ravager.services.google.helpers.controller import GoogleController
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from pathlib import Path
from datetime import datetime, timedelta
import pytz
from ravager.celery_tasks.tasks import app
from telegram import Bot
from ravager.helpers.humanize import humanize
from ravager.database.helpers.structs import UserStruct, OpsDataStruct
from ravager.config import TIMEZONE
import logging

logger = logging.getLogger(__file__)


class Upload:
    def __init__(self):
        self.user = None
        self.task = None
        self.bot = None

    @app.task(name="start_upload", bind=True)
    def upload(self, task):
        self.bot = Bot(token=str(os.environ.get("BOT_TOKEN")))
        try:
            self.task = OpsDataStruct.from_json(task)
        except AttributeError:
            self.task = OpsDataStruct.from_dict(task)
        self.user = UserStruct()
        self.user.user_id = self.task.user_id
        self.user = UserData(user=self.user).get_user()
        self.task = Tasks(task=self.task).get_task()
        user_id = self.task.user_id
        drive_id_dict = json.loads(self.task.drive_id_dict)
        uploaded_files = self.task.uploaded_files
        msg_id = self.task.msg_id
        source_msg_id = self.task.source_msg_id
        file_path = self.task.file_path
        aria_folder_id = file_path.split("/")[-1]
        drive_id_for_parent = drive_id_dict[aria_folder_id][0]

        user_drive_id = self.user.drive_id
        refresh_token = self.user.refresh_token
        n = 0
        if self.user.storage_type == "shared" and user_drive_id != drive_id_for_parent:
            self.bot.delete_message(chat_id=user_id, message_id=msg_id)
            self.bot.send_message(chat_id=user_id, text="Drive account changed,try again",
                                  reply_to_message_id=source_msg_id)
            self.task.status = "aborted"
            Tasks(task=self.task).set_task()
            return

        download = Path(file_path)
        if download.exists():
            download_size = download.stat().st_size
        else:
            self.bot.delete_message(chat_id=user_id, message_id=msg_id)
            self.bot.send_message(chat_id=user_id, text="File not found,could be deleted",
                                  reply_to_message_id=source_msg_id)
            self.task.status = "aborted"
            Tasks(task=self.task).set_task()
            return

        if drive_id_dict[aria_folder_id][0] == "personal":
            try:
                google_auth_creds = GoogleController().credentials_handler(refresh_token=refresh_token)
                drive = build(serviceName="drive", version="v3", credentials=google_auth_creds, cache_discovery=False)
                storage = drive.about().get(fields="storageQuota").execute()["storageQuota"]
                free_space = int(storage["limit"]) - int(storage["usageInDrive"]) - int(5.243 * (10 ** 7))
                if free_space < download_size:
                    self.bot.delete_message(chat_id=user_id, message_id=msg_id)
                    self.bot.send_message(chat_id=user_id, text="Not enough space in google drive",
                                          reply_to_message_id=source_msg_id)
                    self.task.status = "upload failed"
                    Tasks(task=self.task).set_task()
                    return
            except Exception as e:
                logger.error(e)
                self.bot.send_message(chat_id=user_id, text=str(e),
                                      reply_to_message_id=source_msg_id)
                return "Error occurred while checking space"

        # Add check if resuming i.e. notify user that the bot is resuming
        if uploaded_files is None:
            uploaded_files = {}
        else:
            uploaded_files = json.loads(uploaded_files)
            self.bot.delete_message(chat_id=user_id, message_id=msg_id)
            message = self.bot.send_message(chat_id=user_id, text="Resuming Upload", reply_to_message_id=source_msg_id)
            msg_id = self.task.msg_id = message.message_id

        now = old = datetime.now(pytz.timezone(TIMEZONE))
        self.bot.delete_message(chat_id=user_id, message_id=msg_id)
        message = self.bot.send_message(chat_id=user_id, text="Starting Upload", reply_to_message_id=source_msg_id)
        msg_id = self.task.msg_id = message.message_id

        self.task.uploaded_files = json.dumps(uploaded_files)
        Tasks(task=self.task).set_task()

        for (root, directories, files) in os.walk(file_path, topdown=True):
            root_directory = os.path.split(root)[1]
            if str(aria_folder_id) == str(root_directory):
                if drive_id_dict[aria_folder_id][0] == "personal":
                    parent_id = []
                else:
                    parent_id = drive_id_dict[aria_folder_id][0]
            else:
                parent_id = drive_id_dict[str(root_directory)][0]

            if (uploaded_files == {}) or (n not in uploaded_files):
                uploaded_files[n] = [root_directory, {"dirs": [], "files": []}]

            for d in directories:
                if (((root_directory in uploaded_files[n]) and (d not in uploaded_files[n][1]["dirs"]))
                        or (root_directory not in uploaded_files[n])):
                    try:
                        google_auth_creds = GoogleController().credentials_handler(refresh_token=refresh_token)

                        file_metadata = {"mimeType": "application/vnd.google-apps.folder", "name": d,
                                         "parents": [parent_id]}
                        drive = build(serviceName="drive", version="v3", credentials=google_auth_creds,
                                      cache_discovery=False)

                        request = drive.files().create(body=file_metadata, supportsAllDrives=True,
                                                       fields="id").execute()
                        if d in drive_id_dict:
                            drive_id_dict[d].append(request["id"])
                        else:
                            drive_id_dict[d] = [request["id"]]

                        uploaded_files[n][1]["dirs"].append(d)
                        self.task.uploaded_files = json.dumps(uploaded_files)
                        self.task.drive_id_dict = json.dumps(drive_id_dict)
                        self.task.status = "uploading"
                        self.task.start_time = now
                        Tasks(task=self.task).set_task()

                    except Exception as e:
                        logger.error(e)
                        now = datetime.now(pytz.timezone(TIMEZONE))
                        self.task.uploaded_files = json.dumps(uploaded_files)
                        self.task.drive_id_dict = json.dumps(drive_id_dict)
                        self.task.status = "upload failed"
                        self.task.end_time = now
                        Tasks(task=self.task).set_task()
                        self.bot.editMessageText(message_id=msg_id, chat_id=user_id,
                                                 text="Upload Failed,Try Again Manually")

                        return "Failed while creating directory"
            for f in files:
                old_update = 0
                if ((".aria2" not in f) and (
                        ((root_directory in uploaded_files[n]) and (f not in uploaded_files[n][1]["files"]))
                        or (root_directory not in uploaded_files[n]))):

                    google_auth_creds = GoogleController().credentials_handler(refresh_token=refresh_token)
                    file_metadata = {"name": str(f), "parents": [parent_id]}
                    drive = build(serviceName="drive", version="v3", credentials=google_auth_creds,
                                  cache_discovery=False)
                    media = MediaFileUpload(("{}/{}".format(str(root), str(f))), chunksize=256 * 1024, resumable=True)
                    request = drive.files().create(body=file_metadata, media_body=media, supportsAllDrives=True)
                    now = datetime.now(pytz.timezone(TIMEZONE))
                    self.task.status = "uploading"
                    Tasks(task=self.task).set_task()
                    response = None
                    try:
                        while response is None:
                            status, response = request.next_chunk(num_retries=11)
                            if status is None:
                                try:
                                    permission = {"role": "reader", "type": "anyone"}
                                    drive.permissions().create(fileId=str(response["id"]),
                                                               body=permission).execute()
                                except Exception as error:
                                    logger.error(error)
                                uploaded_files[n][1]["files"].append(f)
                                self.task.uploaded_files = json.dumps(uploaded_files)
                                self.task.drive_id_dict = json.dumps(drive_id_dict)
                                Tasks(task=self.task).set_task()
                            else:
                                t = round(status.total_size, 2)
                                c = round(status.resumable_progress, 2)
                                if c != 0:
                                    total = humanize(t)
                                    completed = humanize(c)

                                percent = int((status.resumable_progress * 100) / status.total_size)
                                update_text = "{} {}% uploaded of {} {} / {} {}".format(str(f), percent, completed.size,
                                                                                        completed.unit,
                                                                                        total.size, total.unit)
                                len_update_text = len(update_text.encode("utf-8"))
                                difference = timedelta(seconds=5)
                                now = datetime.now(pytz.timezone(TIMEZONE))
                                if ((int(percent) != int(old_update)) and
                                        (now - old > difference) and
                                        (len_update_text < 512)):
                                    try:
                                        self.bot.edit_message_text(message_id=msg_id, chat_id=user_id, text=update_text)
                                        old = now
                                    except Exception as e:
                                        logger.error(e)
                                    finally:
                                        old_update = percent
                    except Exception as e:
                        logger.error(e)
                        now = datetime.now(pytz.timezone(TIMEZONE))
                        self.task.uploaded_files = json.dumps(uploaded_files)
                        self.task.drive_id_dict = json.dumps(drive_id_dict)
                        self.task.status = "upload failed"
                        self.task.end_time = now
                        self.bot.delete_message(chat_id=user_id, message_id=msg_id)
                        message = self.bot.send_message(chat_id=user_id, text="Upload Failed,Try Again Manually",
                                                        reply_to_message_id=source_msg_id)
                        self.task.msg_id = message.message_id
                        Tasks(task=self.task).set_task()
                        return "Failed while uploading file"
            if n > 1:
                drive_id_dict[root_directory].remove(parent_id)

            if root_directory in drive_id_dict["used_drive_ids"]:
                drive_id_dict["used_drive_ids"][root_directory].append(parent_id)
            else:
                drive_id_dict["used_drive_ids"][root_directory] = [parent_id]
            n += 1

        self.bot.delete_message(chat_id=user_id, message_id=msg_id)
        message = self.bot.send_message(chat_id=user_id, text="Upload Complete", reply_to_message_id=source_msg_id)
        self.task.msg_id = message.message_id
        self.task.uploaded_files = json.dumps(uploaded_files)
        self.task.status = "uploaded"
        Tasks(task=self.task).set_task()
        clean = Tasks().clean()
        return clean

