import logging
import os
import signal

from celery import uuid
from telegram import Bot

from ravager.config import BOT_TOKEN
from ravager.database.helpers.structs import OpsDataStruct
from ravager.database.tasks import Tasks
from ravager.services.aria import aria2c, aria2, start_aria
from ravager.services.aria.updater import Updater
from ravager.services.google.helpers import uploader

logger = logging.getLogger(__file__)


def start(api, gid):
    status = aria2c.tell_status(gid=gid)
    if ("bittorrent" in status and "[METADATA]" not in status["files"][0]["path"]) or ("bittorrent" not in status):
        task = OpsDataStruct()
        task.gid = gid
        file_id = Tasks(task=task, key="gid").get_tasks()[-1].file_id
        task.file_id = file_id
        tasks = Tasks(task=task, key="file_id").get_tasks()
        for t in tasks:
            if t.status == "processing":
                t.task_id = uuid()
                t.status = "downloading"
                message = bot.send_message(chat_id=t.user_id, reply_to_message_id=t.source_msg_id,
                                           text="Download Started")
                msg_id = message.message_id
                bot.delete_message(chat_id=t.user_id, message_id=t.msg_id)
                Tasks(task=t).set_task()
                Updater().download_updater.apply_async(
                    kwargs={"gid": gid, "source_msg_id": t.source_msg_id, "msg_id": msg_id}, task_id=t.task_id)


def complete(api, gid):
    status = aria2c.tell_status(gid=gid)
    task = OpsDataStruct()
    task.gid = gid
    file_id = Tasks(task=task, key="gid").get_tasks()[-1].file_id
    task.file_id = file_id
    tasks = Tasks(task=task, key="file_id").get_tasks()
    if ("bittorrent" in status and "[METADATA]" not in status["files"][0]["path"]) or ("bittorrent" not in status):
        for t in tasks:
            if t.status == "downloading":
                t.status = "downloaded"
                message = bot.send_message(chat_id=t.user_id,
                                           reply_to_message_id=t.source_msg_id,
                                           text="Download Complete")
                file_path = status["dir"]
                t.file_path = file_path
                uploader.upload_file(t, message)
    else:
        for t in tasks:
            gid = status["followedBy"][0]
            t.gid = gid
            Tasks(task=t).set_task()


def pause(api, gid):
    logger.error("Download Pause:")
    logger.error(api)
    logger.error(gid)


def stop(api, gid):
    logger.error("Download Stopped:")
    logger.error(api)
    logger.error(gid)


def error(api, gid):
    logger.error("Download Errored:")
    logger.error(api)
    logger.error(gid)


def signal_handler(s, frame):
    logger.info(s)
    logger.info(frame)
    aria2.stop_listening()
    logger.info("Stopped listening to aria2 notifications")
    os.system("pkill aria2c")
    logger.info("aria2c stopped")
    return


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    start_aria()
    bot = Bot(token=BOT_TOKEN)
    logger.info("aria2c started")
    aria2.listen_to_notifications(threaded=True,
                                  on_download_start=start,
                                  on_download_complete=complete,
                                  on_download_pause=pause,
                                  on_download_stop=stop,
                                  on_download_error=error)
    logger.info("Started listening to aria2 notifications")
