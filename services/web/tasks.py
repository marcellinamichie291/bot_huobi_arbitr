from datetime import datetime, timedelta
import logging
import os
import time

from celery import Celery
from celery.schedules import crontab
from sqlalchemy import and_, func

# from conf import REDIS_PASSWORD
from flaskapp import app as flaskapp
from db import db
from models import Bundle


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
    level=logging.INFO,
    filename='log.log'
    )


def make_celery(app):
    celery = Celery(app.import_name)
    celery.conf.timezone = 'Europe/Moscow'
    celery.conf.update(app.config["CELERY_CONFIG"])

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


app = make_celery(flaskapp)


@app.task
def check_spread():
    for bundle in Bundle.query:
        try:
            print(f'************* SPREAD по связке {bundle.name}: {bundle.spread()}')
        except Exception as exc:
            bundle.status = str(exc)
            db.session.commit()


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):

    # sender.add_periodic_task(
    #     crontab(minute='*/1'),
    #     check_payment.s()
    #     )
    sender.add_periodic_task(1, check_spread.s())
