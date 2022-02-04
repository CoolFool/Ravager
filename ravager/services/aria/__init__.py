import aria2p
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
