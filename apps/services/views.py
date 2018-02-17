# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from apps.services.models import ServiceNode
from ..base.utils import json_response
from .models import Service


@csrf_exempt
def webhook_trigger(request):
    response = json.loads(request.body)
    if response.get('object_kind') == 'push' and response.get('ref') == 'refs/heads/master':
        service = Service.objects.get(gitlab_project_id=response['project_id'], servicenodetype__server_type='STAG')
        service.deploy()

    return HttpResponse(status=200)


# def get_service_uri(request):
#     service_name = request.GET.get('name')
#     service_version = request.GET.get('version')
#     if not service_name and not service_version:
#         return json_response({"error": "GET params name and version cannot null"}, status=400)
#
#     service = ServiceNode.get_service_by_name_version(service_name, service_version)
#     return json_response(service.service_uri, status=200)
