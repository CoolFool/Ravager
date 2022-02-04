from ravager.services.google.helpers import uploader
from ravager.database.helpers.structs import OpsDataStruct
from ravager.database.tasks import Tasks
from ravager.celery_tasks.tasks import app
from ravager.services.aria.download import Download
from telegram.ext import CallbackQueryHandler
import logging

logger = logging.getLogger(__file__)


class AbortAndUpload:
    def __init__(self):
        pass

    def callback_handler(self, update, context):
        callback_data = update.callback_query.data
        callback_data = callback_data.split("|")
        method = callback_data[0]
        action = callback_data[1]
        src_msg_id = callback_data[2]
        task = OpsDataStruct()
        task.source_msg_id = src_msg_id
        task = Tasks(task=task).get_task()
        if method == "upload" and action == "no":
            update.callback_query.edit_message_text(text="Uploading cancelled")
        if method == "upload" and action == "yes":
            upload_msg = update.callback_query.edit_message_text(text="Starting upload")
            uploader.upload_file(task, upload_msg)

        if method == "abort" and action == "yes":
            src_msg_id = callback_data[2]
            abort_msg = update.callback_query.edit_message_text(text="Trying to abort transfer")
            abort_msg_id = abort_msg.message_id
            abort_task = self.abort_task(update, context, task, abort_msg_id)

        if method == "abort" and action == "no":
            update.callback_query.edit_message_text(text="Transfer allowed to process as per request")

    @staticmethod
    def abort_task(update, context, task, abort_msg_id):
        msg_sent = False

        try:
            # update celery task id in db for uploads cause manual upload when completed will use old task id
            download = Download()
            celery_task_id = task.task_id
            user_id = task.user_id
            gid = task.gid
            source_msg_id = task.source_msg_id
            revoke_task = app.control.revoke(celery_task_id, terminate=True, signal="SIGKILL")
            aria_stop_download = download.remove(gid)
            logger.info(aria_stop_download)
            if aria_stop_download:
                # context.bot.delete_message(chat_id=user_id,message_id=latest_message_id)
                context.bot.send_message(chat_id=user_id, text="Task aborted successfully",
                                         reply_to_message_id=source_msg_id)
                task.status = "aborted"
                Tasks(task=task).set_task()
                context.bot.delete_message(chat_id=user_id, message_id=abort_msg_id)
                msg_sent = True
                return task
            else:
                context.bot.delete_message(chat_id=user_id, message_id=abort_msg_id)
                context.bot.send_message(chat_id=user_id, text="Failed to abort task",
                                         reply_to_message_id=source_msg_id)
                msg_sent = True
                logger.error("Failed to abort task", task)
                return
        except Exception as e:
            logger.error(e)
            if str(e) == "GID {} is not found".format(gid):
                context.bot.delete_message(chat_id=user_id, message_id=abort_msg_id)
                context.bot.send_message(chat_id=user_id,
                                         text="Task probably aborted,check if ongoing transfer msg updates",
                                         reply_to_message_id=source_msg_id)
                msg_sent = True
                logger.error("Task probably aborted", task)
                return
            if str(e) == "No such download for GID#{}".format(gid):
                context.bot.delete_message(chat_id=user_id, message_id=abort_msg_id)
                context.bot.send_message(chat_id=user_id,
                                         text="Task probably aborted,check if ongoing transfer msg updates",
                                         reply_to_message_id=source_msg_id)
                msg_sent = True
                logger.error("Task probably aborted", task)
                return
            context.bot.send_message(chat_id=user_id, text="Failed to abort task", reply_to_message_id=source_msg_id)
            msg_sent = True
            logger.error("Failed to abort task", task)
            return
        finally:
            if not msg_sent:
                context.bot.send_message(chat_id=user_id, text="Failed to abort task",
                                         reply_to_message_id=source_msg_id)
                logger.error("Failed to abort task", task)
                return

    def upload_callback_handler(self):
        abort_callback = CallbackQueryHandler(self.callback_handler, pattern="upload")
        return abort_callback

    def abort_callback_handler(self):
        abort_callback = CallbackQueryHandler(self.callback_handler, pattern="abort")
        return abort_callback
