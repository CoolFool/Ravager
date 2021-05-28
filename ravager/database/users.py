from . import sessionmaker, session
from ravager.database.helpers.setup_db import User, Operation, Admin


class UserConfig:
    def __init__(self,*args,**kwargs):
        self.user = session.query(User).filter(User.user_id == "").first()

    def authorize_user(self,user_id):
        return

    def add_user(self,user_id):
        return

    def block_user(self,user_id):
        return

