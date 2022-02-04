import heroku3
import datetime
import logging
from ravager.database.tasks import Tasks
from ravager.config import APP_URL, HEROKU_API_TOKEN
from urllib.parse import urlparse

logger = logging.getLogger(__file__)


def get_ravager():
    heroku_conn = heroku3.from_key(HEROKU_API_TOKEN)
    app_name = urlparse(APP_URL).netloc.split(".")
    if app_name[0] == "www":
        app_name = app_name[1]
    else:
        app_name = app_name[0]
    ravager = heroku_conn.apps()[app_name].dynos()[0]
    return ravager


def restart_required():
    ravager = get_ravager()
    state = ravager.state
    updated_at = ravager.updated_at.replace(tzinfo=None)
    now = datetime.datetime.now()
    diff = datetime.timedelta(hours=6)
    if state == "up" and now - updated_at >= diff:
        return True
    return False


def get_uptime():
    ravager = get_ravager()
    state = ravager.state
    if state == "up":
        now = datetime.datetime.now()
        shutdown_time = ravager.updated_at.replace(tzinfo=None) + datetime.timedelta(hours=24)
        return shutdown_time - now
    else:
        raise SystemExit("Heroku Dyno not up")


def restart_dyno(admin=False):
    if admin or (restart_required() and Tasks().get_active_tasks() <= 0):
        logger.info("Restarting Dyno")
        resp = get_ravager().restart()
        logger.info("Dyno Starting Up")
        clear = Tasks().clear()
        logger.info("Cleared database with {} tasks".format(clear))
        return resp

