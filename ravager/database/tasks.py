from ravager.database import session
from ravager.database.helpers.setup_db import Task
from ravager.database.table import Table
from ravager.database.helpers.structs import OpsDataStruct
from sqlalchemy import asc, or_


class Tasks(Table):
    def __init__(self, task=None, key=None):
        super().__init__(base=Task, struct=task)
        if task is not None:
            self.struct = task
            self.base = Task
            self.tasks = []
            if key is None:
                self.query = session.query(Task).filter(Task.source_msg_id == str(self.struct.source_msg_id)).first()
            else:
                self.query = session.query(Task).filter(getattr(Task, key) == str(getattr(self.struct, key))).order_by(
                    asc(Task.id)).all()
            if self.query is None:
                self.new_row = Task(task_id=self.struct.task_id)

    def get_tasks(self):
        tasks = []
        for i in self.query:
            task = OpsDataStruct()
            for value in task.__dict__.keys():
                setattr(task, value, getattr(i, value))
            tasks.insert(len(tasks), task)
        if not tasks:
            return None
        return tasks

    def get_task(self):
        return Table.get_row(self)

    def set_task(self):
        return Table.set_row(self)

    @staticmethod
    def clean():
        uploaded_tasks = session.query(Task).filter(Task.status == "uploaded").delete()
        session.commit()
        return uploaded_tasks

    @staticmethod
    def clear():
        tasks = session.query(Task).delete()
        session.commit()
        return tasks

    @staticmethod
    def get_active_tasks():
        active_tasks = session.query(Task).filter(or_(Task.status == "uploading"),
                                                  (Task.status == "downloading"),
                                                  (Task.status == "processing"),
                                                  (Task.status == "downloaded")).count()
        session.commit()
        session.close()
        return active_tasks

    def __del__(self):
        session.close()
