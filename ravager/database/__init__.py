from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from ravager.config import DATABASE_URL
import logging
import sys
from ravager.config import LOGS_DIR, LOG_LEVEL

logging.basicConfig(format='"%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s"',
                    level=LOG_LEVEL,
                    handlers=[logging.FileHandler("{}/ravager.log".format(LOGS_DIR)),
                              logging.StreamHandler(sys.stdout)])

engine = create_engine(DATABASE_URL, poolclass=NullPool)
session_maker = sessionmaker(bind=engine)
session = session_maker()
