import os
import logging
from telegram.ext import Updater, PicklePersistence
from dotenv import load_dotenv
load_dotenv("/home/aang/Projects/Ravager/ravager/debug.env")

try:
    REDIS_URL = os.environ["REDIS_URL"]
    TOKEN = os.environ["TOKEN"]
    APP_URL = os.environ["APP_URL"]
    CLIENT_CONFIG = os.environ["CLIENT_CONFIG"]
    DATABASE_URL = os.environ["DATABASE_URL"]
    ROOT_DIR = os.environ["ROOT_DIR"]
    STATE_SECRET_KEY = os.environ["STATE_SECRET_KEY"]
    HEROKU_APP = os.environ["HEROKU_APP"]
except KeyError as e:
    print("Key Not Found: {}".format(e))
    raise SystemError("Setup the bot properly,You dumbass")

logging.basicConfig(format='"%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s"',
                    level=logging.DEBUG,
                    handlers=[logging.FileHandler("{}/logs/ravager.log".format(ROOT_DIR)), logging.StreamHandler()]
                    )

LOGGER = logging.getLogger()

#persistence = PicklePersistence(filename="conversation")
#updater = Updater(token=TOKEN, use_context=True, persistence=persistence)
#dispatcher = updater.dispatcher
