from ravager.database import session
from sqlalchemy.inspection import inspect


class Table:
    def __init__(self, base, struct):
        self.struct = struct
        self.query = None
        self.base = base
        self.row = None
        if not self.query:
            self.new_row = None

    def get_row(self):
        if self.query:
            for value in self.struct.__dict__.keys():
                if self.query:
                    setattr(self.struct, value, getattr(self.query, value))
            return self.struct
        else:
            return None

    def set_row(self):
        if not self.query:
            primary_key = inspect(self.base).primary_key[0].name
            if getattr(self.struct, primary_key) is None and primary_key != "id":
                raise Exception("Value for Primary Key: \"{}\" is required".format(primary_key))
            else:
                for column in self.struct.__dict__.keys():
                    if getattr(self.struct, column) is not None:
                        setattr(self.new_row, column, getattr(self.struct, column))
                session.add(self.new_row)
                session.commit()
        if self.query:
            for value in self.struct.__dict__.keys():
                if getattr(self.struct, value) is not None:
                    setattr(self.query, value, getattr(self.struct, value))
            session.commit()
        return True

    def __del__(self):
        session.close()
