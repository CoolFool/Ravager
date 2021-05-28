import psutil


class Process:
    def __init__(self, process_name):
        self.process_name = process_name

    def check_process(self):
        for proc in psutil.process_iter():
            try:
                if self.process_name.lower() in proc.name().lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass


