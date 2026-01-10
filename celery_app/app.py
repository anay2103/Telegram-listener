from celery import Celery
from celery.schedules import crontab

from bot.settings import build_redis_uri

from .tasks import delete_old_vacancies, poll_hh

app = Celery()

app.conf.update(broker_url=build_redis_uri())
app.add_periodic_task(schedule=crontab(minute='*/30'), sig=poll_hh.s())
app.add_periodic_task(schedule=crontab(minute=0, hour=0, day_of_week='sun'), sig=delete_old_vacancies.s())
