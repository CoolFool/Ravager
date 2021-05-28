from . import sessionmaker, session
from ravager.database.helpers.setup_db import User, Operation, Admin


class AdminConfig:
    def __init__(self,*args,**kwargs):
        self.admin = session.query(Admin).filter(Admin.user_id == "admin").first()

    def add_admin(self,user_id):
        return

    def allow_user(self,user_id):
        return

    def block_user(self,user_id):
        return

    def is_valid_user(self,user_id):
        return

    def toggle_allow_admin(self):
        return

    def get_allow_admin_status(self):
        return

    def update_limits(self,**kwargs):
        return

    def update_filter_config(self,**kwargs):
        return
