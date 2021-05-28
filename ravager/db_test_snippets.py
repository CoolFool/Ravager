import sys

sys.path.append("../")
from ravager.database.helpers import setup_db
setup_db.create_tables()
setup_db.insert_default_admin_conf()
