from telegram.ext import CommandHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from ravager.bot.helpers.validators import *
from ravager.database.tasks import Tasks
from ravager.database.helpers.structs import OpsDataStruct
from ravager.services.google.helpers import uploader


class Upload:
    def __init__(self):
        pass

    @check_authorized()
    @check_drive_selection()
    @check_celery_queue()
    def manual_upload(self, update, context):
        chat_id = update.effective_chat.id
        if update.message.reply_to_message is not None:
            reply_msg_id = update.message.reply_to_message.message_id
            task = OpsDataStruct()
            task.source_msg_id = reply_msg_id
            task = Tasks(task=task).get_task()
            if task is not None:
                status = task.status
                try:
                    if status == "processing":
                        context.bot.send_message(chat_id=chat_id, reply_to_message_id=reply_msg_id,
                                                 text="Download not yet started or Invalid Data")
                    elif status == "error occurred while gathering data":
                        context.bot.send_message(chat_id=chat_id, reply_to_message_id=reply_msg_id,
                                                 text="Invalid request")
                    else:
                        source_msg_id = task.source_msg_id
                        if status == "downloading":
                            context.bot.send_message(chat_id=chat_id, reply_to_message_id=source_msg_id,
                                                     text="Ongoing Download,Can't Upload yet")
                        elif (status == "downloaded") or (status == "uploading") or status == "download complete":
                            context.bot.send_message(chat_id=chat_id, reply_to_message_id=source_msg_id,
                                                     text="Ongoing Upload,Patience!")
                        elif status == "upload failed":
                            upload_msg = context.bot.send_message(chat_id=chat_id, reply_to_message_id=source_msg_id,
                                                                  text="Resuming Upload")
                            uploader.upload_file(task,upload_msg)

                        elif status == "uploaded":
                            drive_options = [
                                [InlineKeyboardButton(text="Yes", callback_data="upload|yes|{}".format(source_msg_id)),
                                 InlineKeyboardButton(text="No", callback_data="upload|no|{}".format(source_msg_id))]]
                            reply_markup = InlineKeyboardMarkup(drive_options)
                            context.bot.send_message(chat_id=chat_id, reply_to_message_id=source_msg_id,
                                                     text="Are you sure about uploading again?",
                                                     reply_markup=reply_markup)
                        elif status == "aborted":
                            context.bot.send_message(chat_id=chat_id, reply_to_message_id=reply_msg_id,
                                                     text="The following transfer was aborted,can't upload")

                        else:
                            context.bot.send_message(chat_id=chat_id, reply_to_message_id=reply_msg_id,
                                                     text="Error occurred while uploading")

                except Exception as e:
                    logger.error(e)
                    context.bot.send_message(chat_id=chat_id, reply_to_message_id=reply_msg_id,
                                             text="Error occurred while uploading,maybe invalid message?")

    def upload_handler(self):
        manual_upload_handler = CommandHandler("upload", self.manual_upload)
        return manual_upload_handler
