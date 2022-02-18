import sys

import telegram
from flask import Flask, request, redirect
from google_auth_oauthlib.flow import Flow
import json
import os
from googleapiclient.discovery import build
from telegram import Bot
from queue import Queue
from threading import Thread
from telegram.ext import Dispatcher, PicklePersistence
from telegram.ext.jobqueue import JobQueue
import logging
import signal
from ravager.database.users import UserData
from ravager.database.helpers.structs import UserStruct
from ravager.bot.commands.start import Start
from ravager.bot.commands.add_drive import AddDrive
from ravager.bot.commands.download import Download
from ravager.bot.commands.revoke import Revoke
from ravager.bot.commands.upload import Upload
from ravager.bot.commands.abort import Abort
from ravager.bot.helpers.abort_upload_handler import AbortAndUpload
from ravager.bot.commands.admin_interface import AdminInterface
from ravager.bot.commands.help import Help
from ravager.bot.commands.unknown import Unknown
from ravager.bot.commands.error import error_handler
from ravager.config import APP_URL, BOT_TOKEN, CLIENT_CONFIG, PORT, BOT_URL, OAUTH_URL, ROOT_DIR, LOGS_DIR
from ravager.services.google.helpers.controller import GoogleController

app = Flask(__name__)

REDIRECT_URI = OAUTH_URL + "/oauth_handler"
TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = APP_URL + "/" + TOKEN


@app.route("/")
def index():
    return redirect(BOT_URL)


@app.route("/keep_alive")
def keep_alive():
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/oauth_handler')
def oauth_handler():
    code = request.args.get("code")
    state = request.args.get("state")
    user = UserStruct(state=state)
    user = UserData(user=user).get_user()
    chat_id = user.user_id
    try:
        flow = Flow.from_client_config(
            client_config=CLIENT_CONFIG,
            scopes=['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/drive.metadata'])
        flow.redirect_uri = REDIRECT_URI
        Flow.fetch_token(flow, code=code)
        creds = flow.credentials.to_json()
        creds = json.loads(creds)
        logger.info(creds)
        print(creds)
    except Exception as e:
        logger.error(e)
        UserData().delete_user("state", state)
        bot.send_message(chat_id=chat_id, text="Authorization Failed,Revoke access from google account if authorized")
        return redirect(BOT_URL)

    try:
        refresh_token = creds["refresh_token"]
        user.refresh_token = refresh_token
        user.authorized = True
        Thread(target=user_config, args=(user,)).start()
        return redirect(BOT_URL)
    except Exception as e:
        logger.error(e)
        logger.info(user)
        UserData().delete_user("state", state)
        bot.send_message(chat_id=chat_id,
                         text="Authorization Failed,Revoke access from google account if authorized")
        return redirect(BOT_URL)


@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    update = telegram.update.Update.de_json(request.get_json(force=True), bot=bot)
    update_queue.put(update)
    return 'OK'


def user_config(user):
    google_auth_creds = GoogleController().credentials_handler(refresh_token=user.refresh_token)
    drive = build(serviceName="drive", version="v3", credentials=google_auth_creds, cache_discovery=False)
    email = drive.about().get(fields="user").execute()
    email = email["user"]["emailAddress"]
    user.email = email
    UserData(user=user).set_user()
    chat_id = user.user_id
    bot.send_message(chat_id=chat_id, text="Authorization Successful")
    UserData().update_users("email", user.email, "refresh_token", user.refresh_token)
    return


def signal_handler(s, frame):
    logger.info("Shutting down bot please wait")
    os.remove(ROOT_DIR + "/ravager/conversation")
    logger.info("Deleted bot saved conversation")
    dispatch.stop()
    logger.info("Dispatcher stopped")
    sys.exit(0)


def setup():
    bot.set_webhook(url=WEBHOOK_URL)
    telegram_update_queue = Queue()
    job_queue = JobQueue()
    persistence = PicklePersistence(filename="conversation")
    dispatcher = Dispatcher(bot, telegram_update_queue, persistence=persistence, job_queue=job_queue)
    job_queue.set_dispatcher(dispatcher=dispatcher)
    job_queue.start()

    start = Start()
    add_drive = AddDrive()
    download = Download()
    revoke = Revoke()
    upload = Upload()
    abort = Abort()
    help_cmd = Help()
    abort_upload_callback = AbortAndUpload()
    admin_interface = AdminInterface()
    unknown = Unknown()

    dispatcher.add_handler(start.authorization_convo_handler())
    dispatcher.add_handler(add_drive.default_convo_handler())
    dispatcher.add_handler(download.download_convo_handler())
    dispatcher.add_handler(revoke.revoke_handler())
    dispatcher.add_handler(revoke.revoke_callback_handler())
    dispatcher.add_handler(upload.upload_handler())
    dispatcher.add_handler(abort.abort_handler())
    dispatcher.add_handler(help_cmd.help_handler())
    dispatcher.add_handler(admin_interface.admin_interface_handler())
    dispatcher.add_handler(abort_upload_callback.upload_callback_handler())
    dispatcher.add_handler(abort_upload_callback.abort_callback_handler())
    dispatcher.add_handler(start.reply_msg_handler())
    dispatcher.add_handler(unknown.unknown_handler())
    dispatcher.add_error_handler(error_handler)

    telegram_thread = Thread(target=dispatcher.start, name='dispatcher')
    telegram_thread.start()

    return telegram_update_queue, job_queue, dispatcher


bot = Bot(token=str(BOT_TOKEN))
update_queue, job, dispatch = setup()
logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)
signal.signal(signal.SIGINT, signal_handler)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
