import logging

from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import call_command

_scheduler = None


def _sync_calendar():
    call_command("sync_calendar")


def start_scheduler():
    global _scheduler
    if _scheduler:
        return

    logging.getLogger("apscheduler").setLevel(logging.WARNING)

    scheduler = BackgroundScheduler()
    scheduler.add_job(_sync_calendar, "interval", hours=1, id="sync_calendar")
    scheduler.start()
    _scheduler = scheduler
