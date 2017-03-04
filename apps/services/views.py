# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Service


@csrf_exempt
def webhook_trigger(request):
    response = json.loads(request.body)
    print request.META
    if response.get('object_kind') == 'tag_push':
        service = Service.objects.get(gitlab_project_id=response['project_id'])
        service.deploy()

    return HttpResponse(status=200)
