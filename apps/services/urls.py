from django.conf.urls import url

from .views import *

app_name = 'services'

urlpatterns = [
    url(r'^trigger/$', webhook_trigger, name='webhook_trigger'),
    url(r'^uri/$', get_service_uri, name='get_service_uri'),
]
