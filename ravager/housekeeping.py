from ravager.database.tasks import Tasks
import logging
from ravager.database.helpers import setup_db
from ravager.config import DATABASE_URL, LOGS_DIR
from ravager.helpers.check_process import Process
from subprocess import check_call

logger = logging.getLogger(__file__)

setup_db.create_tables()
logger.info("Database setup at {}".format(DATABASE_URL))

logger.info(Tasks().clear())


def start_aria():
    # "input-file": "{}/session.txt".format(LOGS_DIR)
    aria2_command = []
    aria2_command.append("aria2c")
    aria2_command.append("--enable-rpc=true")
    aria2_command.append("--daemon=true")
    aria2_command.append("--max-tries=5")
    aria2_command.append("--retry-wait=30")
    aria2_command.append("--rpc-listen-all=true")
    aria2_command.append("--rpc-listen-port=6801")
    aria2_command.append("--rpc-secret=qwerty")
    # aria2_command.append("--save-session={}/session.txt".format(LOGS_DIR))
    aria2_command.append("--log={}/aria2.log".format(LOGS_DIR))
    aria2_command.append("--save-session-interval=20")
    aria2_command.append("--timeout=600")
    aria2_command.append("--bt-force-encryption=false")
    aria2_command.append("--seed-time=0.01")
    aria2_command.append("--log-level=notice")
    aria2_command.append("--bt-stop-timeout=21600")
    aria2_command.append("--auto-file-renaming=false")
    # aria2_command.append("--force-save=true")
    # aria2_command.append("--allow-overwrite=true")
    aria2_command.append("--continue=true")
    aria2_command.append("--bt-enable-hook-after-hash-check=false")
    aria2_command.append("--auto-save-interval=60")
    aria2_command.append("--rpc-save-upload-metadata=false")

    aria2_status = Process(process_name="aria2c").check_process()
    if not aria2_status:
        check_call(aria2_command)
    return True


logger.info(start_aria())
logger.info("aria2c started")
