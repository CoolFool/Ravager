import ast
import os
from os.path import dirname
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__file__)
load_dotenv()
"""
CRITICAL 50
ERROR 40
WARNING 30
INFO 20
DEBUG 10
NOTSET 0
"""
try:
    ROOT_DIR = str(dirname(dirname(os.path.abspath(__file__))))
    DATABASE_DIR = ROOT_DIR + "/database"
    DOWNLOAD_DIR = str(os.environ.get("DOWNLOAD_DIR", ROOT_DIR + "/downloads"))
    LOGS_DIR = str(os.environ.get("LOGS_DIR", ROOT_DIR + "/logs"))
    DEFAULT_DB_URL = "sqlite:///" + DATABASE_DIR + "/ravager.db?check_same_thread=False"
    APP_URL = str(os.environ["APP_URL"])
    OAUTH_URL = str(os.environ.get("OAUTH_URL", APP_URL))
    CLIENT_CONFIG = ast.literal_eval(os.environ["CLIENT_CONFIG"])
    DATABASE_URL = str(os.environ.get("DATABASE_URL", DEFAULT_DB_URL))
    REDIS_URL = str(os.environ["REDIS_URL"])
    BOT_TOKEN = str(os.environ["BOT_TOKEN"])
    STATE_SECRET_KEY = str(os.environ["STATE_SECRET_KEY"])
    BOT_URL = str(os.environ["BOT_URL"])
    HEROKU_APP = os.getenv("HEROKU_APP", 'False').lower() in ('true', '1', 't')
    KEEP_HEROKU_ALIVE = os.getenv("KEEP_HEROKU_ALIVE", 'False').lower() in ('true', '1', 't')
    HEROKU_API_TOKEN = str(os.getenv("HEROKU_API_TOKEN"))
    ALLOWLIST = os.getenv("ALLOWLIST", 'True').lower() in ('true', '1', 't')
    GROUP_PASSWORD = str(os.environ["GROUP_PASSWORD"])
    USER_PASSWORD = str(os.environ["USER_PASSWORD"])
    MAX_TASKS_PER_USER = int(os.environ.get("MAX_TASKS_PER_USER", 2))
    TIMEZONE = str(os.environ.get("TIMEZONE", "UTC"))
    PORT = int(os.environ.get("PORT", 8443))
    LOG_LEVEL = int(os.environ.get("LOG_LEVEL", 20))
    STORAGE_SIZE = int(os.environ.get("STORAGE_SIZE", 0))
    STORAGE_TIME = int(os.environ.get("STORAGE_TIME", 0))
    if HEROKU_APP and DATABASE_URL == DEFAULT_DB_URL:
        raise SystemError("SQLite not allowed on Heroku")
except KeyError as e:
    logger.error("{} ENV VAR Not Found".format(e))
    raise SystemError("Setup the bot properly")

if __name__ == "__main__":
    if not os.path.exists(LOGS_DIR):
        os.mkdir(LOGS_DIR)
        logger.info("Logs directory created at {}".format(LOGS_DIR))
    else:
        logger.info("Logs directory exists at {}".format(LOGS_DIR))
    if not os.path.exists(DOWNLOAD_DIR):
        os.mkdir(DOWNLOAD_DIR)
        logger.info("Downloads directory created at {}".format(DOWNLOAD_DIR))
    else:
        logger.info("Downloads directory exists at {}".format(DOWNLOAD_DIR))
    if not os.path.exists(DATABASE_DIR):
        os.mkdir(DATABASE_DIR)
        logger.info("Database directory created at {}".format(DATABASE_DIR))
    else:
        logger.info("Database directory exists at {}".format(DATABASE_DIR))
    if DATABASE_URL == DEFAULT_DB_URL:
        from ravager.database.helpers import setup_db
        setup_db.create_tables()
        logger.info("SQLite database created at {}".format(DATABASE_DIR))
    else:
        logger.info("SQLite database exist at {}".format(DATABASE_DIR))



