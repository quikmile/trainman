from django.conf.urls import url

from .views import *

app_name = 'services'

urlpatterns = [
    url(r'^trigger/$', webhook_trigger, name='webhook_trigger'),
]
