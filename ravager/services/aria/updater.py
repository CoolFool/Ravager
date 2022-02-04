import os

from ravager.services.aria import aria2c
from ravager.helpers.humanize import humanize
from ravager.celery_tasks.tasks import app
from ravager.database.tasks import Tasks
from ravager.database.helpers.structs import OpsDataStruct
from ravager.config import TIMEZONE
from telegram import Bot
from datetime import datetime, timedelta
import pytz
import logging

logger = logging.getLogger(__file__)


class Updater:
    def __init__(self):
        self.gid = None
        self.task = None
        self.bot = None

    @app.task(name="download_updater", bind=True)
    def download_updater(self, gid, msg_id, source_msg_id):
        self.bot = Bot(token=os.environ.get("BOT_TOKEN"))
        print(gid)
        status = aria2c.tell_status(gid=gid)
        print(status)
        self.task = OpsDataStruct()
        self.task.source_msg_id = str(source_msg_id)
        self.task = Tasks(task=self.task).get_task()
        chat_id = str(self.task.user_id)
        self.task.file_path = status["dir"]
        Tasks(task=self.task).set_task()
        old = 0
        old_time = datetime.now(pytz.timezone(TIMEZONE))
        while True:
            status = aria2c.tell_status(gid=gid)
            current_status = status["status"]
            match current_status:
                case "active":
                    total = humanize(int(status["totalLength"]))
                    completed = humanize(int(status["completedLength"]))
                    dl_speed = humanize(int(status["downloadSpeed"]))
                    difference = timedelta(seconds=5)
                    if total.size > 0:
                        now = datetime.now(pytz.timezone(TIMEZONE))
                        percent = (completed.original * 100) // total.original
                        update_text = f"{percent}% completed | remaining {completed.size:.2f} {completed.unit}/{total.size:.2f} {total.unit} | " \
                                      f"Downloading at {dl_speed.size:.2f} {dl_speed.unit}ps "
                        len_update_text = len(update_text.encode("utf-8"))
                        if (percent != old) and (now - old_time > difference) and (len_update_text < 512):
                            try:
                                self.bot.edit_message_text(chat_id=chat_id, message_id=msg_id,
                                                           text=update_text)
                                old_time = now
                            except Exception as e:
                                logger.error(e)
                            finally:
                                old = percent

                case "paused":
                    self.bot.delete_message(chat_id=chat_id, message_id=msg_id)
                    break
                case "waiting":
                    self.bot.delete_message(chat_id=chat_id, message_id=msg_id)
                    break
                case "error":
                    self.bot.delete_message(chat_id=chat_id, message_id=msg_id)
                    break
                case "removed":
                    self.bot.delete_message(chat_id=chat_id, message_id=msg_id)
                    break
                case "complete":
                    self.bot.delete_message(chat_id=chat_id, message_id=msg_id)
                    break
                case _:
                    self.bot.delete_message(chat_id=chat_id, message_id=msg_id)
                    break
