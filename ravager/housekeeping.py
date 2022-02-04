from ravager.database.tasks import Tasks
import logging
from ravager.database.helpers import setup_db
from ravager.config import DATABASE_URL

logger = logging.getLogger(__file__)

setup_db.create_tables()
logger.info("Database setup at {}".format(DATABASE_URL))

logger.info(Tasks().clear())

    
