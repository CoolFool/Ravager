import logging
import sys
from .config import LOGS_DIR, LOG_LEVEL

logging.basicConfig(format='"%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s"',
                    level=LOG_LEVEL,
                    handlers=[logging.FileHandler("{}/ravager.log".format(LOGS_DIR)),
                              logging.StreamHandler(sys.stdout)])
