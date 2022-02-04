from ravager.database.helpers.setup_db import User
from ravager.database import session
from sqlalchemy import or_, update
from ravager.database.table import Table


class UserData(Table):
    def __init__(self, user=None):
        if user is not None:
            super().__init__(base=User, struct=user)
            self.query = session.query(User).filter(
                or_(User.user_id == str(user.user_id),
                    User.tg_username == str(user.tg_username),
                    User.state == str(user.state))).first()

            if not self.query:
                self.new_row = User(user_id=user.user_id)

    def get_user(self):
        return Table.get_row(self)

    def set_user(self):
        return Table.set_row(self)

    @staticmethod
    def update_users(key, value, new_key, new_value):
        update_all = session.query(User).filter(getattr(User, key) == value).update({new_key: new_value})
        session.commit()
        return update_all

    @staticmethod
    def get_num_of_users():
        return session.query(User).count()

    @staticmethod
    def delete_user(key, value):
        delete_all = session.query(User).filter(getattr(User, key) == value).delete()
        session.commit()
        return delete_all

    def __del__(self):
        session.close()
