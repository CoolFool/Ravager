import os
import signal
import subprocess
from threading import Timer
import ravager.services.mega.helpers.errors as errors
from ravager.helpers.check_process import Process


class Mega:
    def __init__(self):
        self.notify_chat = ""
        self.update_chat = ""
        self._communicate_timeout = 30
        self._initial_read_timeout = 60
        self._read_timeout = 120

    def _read_timeout_thread(self, proc, timeout):
        return Timer(float(timeout), self._kill_mega_process, kwargs={"proc": proc})

    def _kill_mega_process(self, proc):
        os.kill(proc.pid, signal.SIGKILL)
        self.cancel_all_transfers()
        self._restart_mega()

    @staticmethod
    def _restart_mega():
        mega_server_status = Process(process_name="mega-cmd-server").check_process()
        if mega_server_status:
            try:
                exit_mega = subprocess.run(["mega-exec", "exit"]).returncode
                print(exit_mega)
                if not exit_mega:
                    subprocess.Popen(["mega-cmd-server"], close_fds=True)
                else:
                    raise errors.MegaStandardError("Error starting mega cmd server")
            except subprocess.CalledProcessError:
                raise errors.MegaStandardError("Error exiting mega cmd server")
        else:
            try:
                subprocess.Popen(["mega-cmd-server"], close_fds=True)
            except Exception as e:
                print(e)
                raise errors.MegaStandardError("Error starting mega cmd server")

    @staticmethod
    def _run_mega_command(command):
        kwargs = dict(stdout=subprocess.PIPE,
                      stderr=subprocess.STDOUT,
                      universal_newlines=True,
                      timeout=30)
        process = subprocess.run(command, **kwargs)
        ret_code = process.returncode
        stdout = process.stdout
        if not ret_code:
            return stdout
        else:
            raise errors.MegaRequestError(message=ret_code)

    def login(self, username=None, password=None):
        login_proc = self._run_mega_command(command=["mega-exec", "login", username, password])
        return login_proc

    def logout(self):
        logout_proc = self._run_mega_command(command=["mega-exec", "logout"])
        return logout_proc

    def download(self, download_url, download_path):
        kwargs = dict(bufsize=0,
                      stdout=subprocess.PIPE,
                      stderr=subprocess.STDOUT,
                      universal_newlines=True)
        args = ["mega-exec", "get", download_url, download_path]

        with subprocess.Popen(args, **kwargs) as proc:
            initial_read_timeout = self._read_timeout_thread(proc=proc, timeout=self._initial_read_timeout)
            initial_read_timeout.start()
            output = proc.stdout

            for line in output:
                initial_read_timeout.cancel()
                read_timeout = self._read_timeout_thread(proc=proc, timeout=self._read_timeout)
                read_timeout.start()
                status = line[line.find("(") + 1:line.find(")")].replace(":", "").replace("%", "").split()
                if len(status) == 3:
                    print(status)
                read_timeout.cancel()

        if not proc.returncode:
            return True
        else:
            raise errors.MegaRequestError(message=proc.returncode)

    def download_through_proxy(self, download_url, download_path):
        email, logged_in = self.whoami()
        if logged_in:
            self.logout()
        self.set_proxy(proxy_url="127.0.0.1")
        self.download(download_url=download_url, download_path=download_path)

    def cancel_all_transfers(self):
        cancel_all_proc = self._run_mega_command(command=["mega-exec", "transfers", "-c", "-a"])
        return cancel_all_proc

    def whoami(self):
        whoami_proc = self._run_mega_command(command=["mega-exec", "whoami"])
        email = whoami_proc.decode("utf-8").split()
        return email

    def kill_all_session(self):
        kill_all_session_cmd = self._run_mega_command(command=["mega-exec","killsession","-a"])
        return kill_all_session_cmd

    def set_proxy(self, proxy_url):
        set_proxy_proc = self._run_mega_command(command=["mega-exec", "proxy", proxy_url])
        return set_proxy_proc

    def unset_proxy(self):
        unset_proxy_proc = self._run_mega_command(command=["mega-exec", "proxy", "--none"])
        return unset_proxy_proc
