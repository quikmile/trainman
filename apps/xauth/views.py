import importlib
import json

from django.contrib.auth import authenticate, login, logout
from django.db.models.aggregates import Count
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import parsers, renderers
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.apps import apps

from .authentication import XTokenAuthentication
from ..custom.mixins import GeneralLoginRequiredMixin
from ..orders.models import Order


class ObtainAuthToken(APIView):
    throttle_classes = ()
    permission_classes = ()
    authentication_classes = (XTokenAuthentication,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        return Response({'token': user.token})


obtain_auth_token = ObtainAuthToken.as_view()


class TestView(APIView):
    authentication_classes = (XTokenAuthentication,)
    permission_classes = (IsAdminUser,)

    def get(self, request):
        data = {
            'user': request.user.username,
            'created': request.user.created,
            'token': request.user.token
        }
        return Response(data)


class LoginView(APIView):
    template_name = 'xauth/login.html'

    def get(self, request):
        if request.user.is_authenticated():
            url = request.GET.get('next', '/')
            return HttpResponseRedirect(url)
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        user = authenticate(username=request.POST['username'], password=request.POST['password'])

        if user is not None:
            if user.is_active:
                login(request, user)
                url = request.GET.get('next', '/')
                return HttpResponseRedirect(url)
            else:
                error = "The password is valid, but the account has been disabled!"

                return render(request, self.template_name, {'error': error})
        else:
            error = "The username and password were incorrect."

            return render(request, self.template_name, {'error': error})


def logout_user(request):
    logout(request)
    return HttpResponseRedirect(settings.LOGIN_URL)


class DashboardView(GeneralLoginRequiredMixin, APIView):
    template_name = 'xauth/dashboard.html'

    def get(self, request):
        context = dict()

        order_count = Order.objects.values('shipment__status').annotate(count=Count('id'))
        context['total_orders'] = sum([i['count'] for i in order_count])

        try:
            context['new_orders'] = [i['count'] for i in order_count if i['shipment__status'] == 'PEN'][0]
        except:
            context['new_orders'] = 0

        try:
            context['in_transit_orders'] = [i['count'] for i in order_count if i['shipment__status'] == 'IT'][0]
        except:
            context['in_transit_orders'] = 0

        try:
            context['delivered_orders'] = [i['count'] for i in order_count if i['shipment__status'] == 'DEL'][0]
        except:
            context['delivered_orders'] = 0

        params = dict()
        if request.user.role == 'client':
            params['client__client'] = request.user.client.client

        context['orders'] = Order.objects.filter(**params).select_related('shipment',
                                                                          'client',
                                                                          'pickup_address',
                                                                          'delivery_address',
                                                                          'order_type')[:10]
        return render(request, self.template_name, context=context)


class DataTableView(GeneralLoginRequiredMixin, APIView):
    @csrf_exempt
    def post(self, request):
        params = json.loads(request.GET.get('params', {}))
        limit = request.GET.get('length', 10)
        offset = request.GET.get('start', 0)

        app = request.GET.get('app')
        model = request.GET.get('model')

        Model = apps.get_model(app_label=app, model_name=model.lower())
        module = importlib.import_module('apps.{}.serializers'.format(app))
        Serializer = getattr(module, '{}Serializer'.format(model))

        queryset = Model.objects.filter(**params)[offset:limit]
        serializer = Serializer(queryset, many=True)

        response = dict()
        response['data'] = serializer.data
        response['draw'] = request.GET.get('draw', 1)
        response['recordsTotal'] = request.GET.get('recordsTotal', Model.objects.all().count())
        response['recordsFiltered'] = request.GET.get('recordsFiltered', Model.objects.filter(**params).count())

        return Response(response)
