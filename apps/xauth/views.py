import importlib
import json

from django.contrib.auth import authenticate, login, logout
from django.db.models.aggregates import Count
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.apps import apps

from ..xauth.models import XUser
from .authentication import XTokenAuthentication
from ..custom.mixins import GeneralLoginRequiredMixin

XUser.objects.create()