from celery import Celery
from ravager.config import REDIS_URL, HEROKU_APP, HEROKU_API_TOKEN, KEEP_HEROKU_ALIVE, APP_URL
from ravager.database.tasks import Tasks
from celery.schedules import crontab
import requests
from ravager.helpers.heroku import restart_dyno

app = Celery("Essential Bot Tasks",
             broker=REDIS_URL,
             backend=REDIS_URL,
             )
app.conf.broker_pool_limit = 0


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute=0, hour='*/4'),
        clean_database.s(),
        name="clear_finished_downloads"
    )
    if HEROKU_APP and KEEP_HEROKU_ALIVE:
        sender.add_periodic_task(
            crontab(minute='*/5'),
            keep_heroku_alive.s(),
            name="keep heroku free dyno alive"
        )
    if HEROKU_APP and HEROKU_API_TOKEN is not None:
        sender.add_periodic_task(
            crontab(minute='*/15'),
            restart_heroku.s(),
            name="Restart dyno to reset sleep time"
        )


@app.task()
def clean_database():
    clean = Tasks().clean()
    return clean


@app.task()
def keep_heroku_alive():
    is_alive = requests.get(APP_URL + "/keep_alive")
    return is_alive.status_code


@app.task()
def restart_heroku():
    resp = restart_dyno()
    return resp


app.autodiscover_tasks(["ravager.services.aria.download",
                        "ravager.services.aria.updater",
                        "ravager.services.google.upload"])
