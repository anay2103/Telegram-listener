from celery import Celery
from celery.schedules import crontab

from bot.settings import build_redis_uri

from .tasks import poll_hh

app = Celery()

app.conf.update(broker_url=build_redis_uri())
app.add_periodic_task(schedule=crontab(minute='*/3'), sig=poll_hh.s())
