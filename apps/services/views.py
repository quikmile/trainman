# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from .models import Service


def webhook_trigger(request):
    response = json.loads(request.body)
    print request.META.get('X-Gitlab-Event')
    print response
    if response['object_kind'] == 'tag_push':
        service = Service.objects.get(gitlab_project_id=response['project_id'])
        service.deploy()
