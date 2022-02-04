from subprocess import check_call
import aria2p
from ravager.helpers.check_process import Process
import logging
import sys
from ravager.config import LOGS_DIR, LOG_LEVEL

logging.basicConfig(format='"%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s"',
                    level=LOG_LEVEL,
                    handlers=[logging.FileHandler("{}/ravager.log".format(LOGS_DIR)),
                              logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__file__)

aria2c = aria2p.Client(
    host="http://0.0.0.0",
    port=6801,
    secret="qwerty"
)
aria2 = aria2p.API(aria2c)


def start_aria():
    aria_global_options = {"log": "{}/aria2.log".format(LOGS_DIR)}
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
    #aria2_command.append("--save-session={}/session.txt".format(LOGS_DIR))
    aria2_command.append("--save-session-interval=20")
    aria2_command.append("--timeout=600")
    aria2_command.append("--bt-force-encryption=true")
    aria2_command.append("--seed-time=0.01")
    aria2_command.append("--log-level=notice")
    aria2_command.append("--bt-stop-timeout=21600")
    aria2_command.append("--auto-file-renaming=false")
    #aria2_command.append("--force-save=true")
    #aria2_command.append("--allow-overwrite=true")
    aria2_command.append("--continue=true")
    aria2_command.append("--bt-enable-hook-after-hash-check=false")
    aria2_command.append("--auto-save-interval=60")
    aria2_command.append("--rpc-save-upload-metadata=false")

    aria2_status = Process(process_name="aria2c").check_process()
    if not aria2_status:
        check_call(aria2_command)
    aria2.set_global_options(aria_global_options)
    return True
