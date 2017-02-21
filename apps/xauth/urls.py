from django.conf.urls import patterns, url

from .views import *

urlpatterns = patterns('apps.xauth.views',
                       url(r'^token/$', obtain_auth_token),
                       url(r'^test/$', TestView.as_view()),
                       url(r'^login/$', LoginView.as_view()),
                       url(r'^logout/$', logout_user),
                       url(r'^$', DashboardView.as_view()),
                       url(r'^serializer/$', DataTableView.as_view()),
                       )
