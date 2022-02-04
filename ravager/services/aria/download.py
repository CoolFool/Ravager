from ravager.services.aria import *
from ravager.celery_tasks.tasks import app
from ravager.database.helpers.structs import OpsDataStruct


class Download:
    def __init__(self):
        self.aria2_struct = None
        self.uri = None
        self.download_dir = None
        self.task = None

    @app.task(name="start_download", bind=True)
    def start(self, uri, task):
        self.uri = uri
        self.task = OpsDataStruct.from_json(task)
        aria = aria2.add_uris(uris=[self.uri], options={"dir": self.task.file_path, "gid": self.task.gid})
        logger.info(aria)
        return task

    def pause(self, gid):
        aria2.pause(downloads=[gid])
        return self.__dict__

    @staticmethod
    def remove(gid):
        aria_stop_download = aria2.get_download(gid=gid)
        remove_download = aria2.remove([aria_stop_download], force=True, clean=False)
        return remove_download

    def resume(self, gid):
        aria2.resume(downloads=[gid])
        return self.__dict__
