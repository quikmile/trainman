from __future__ import absolute_import

import os

from celery import Celery
from slacker_log_handler import SlackerLogHandler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trainman.settings')

from django.conf import settings
from celery.signals import after_setup_task_logger, after_setup_logger

app = Celery('trainman')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


def after_setup_logger_handler(sender=None, logger=None, loglevel=None,
                               logfile=None, format=None,
                               colorize=None, **kwds):
    handler = SlackerLogHandler(channel='#infra', api_key=settings.SLACK_TOKEN, username='Trainman Logger')
    handler.setLevel(level='INFO')
    logger.addHandler(handler)


after_setup_logger.connect(after_setup_logger_handler)
after_setup_task_logger.connect(after_setup_logger_handler)
