from django.contrib.auth import logout
from django.http.response import HttpResponseRedirect
from django.conf import settings

from ..base.utils import get_json_response


class GeneralLoginRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.is_ajax():
            pass
        if not request.user.is_authenticated():
            logout(request)
            if request.is_ajax():
                return get_json_response({'status': 403, 'error_msg': 'login required'})
            else:
                return HttpResponseRedirect(settings.LOGIN_URL + '?next=%s' % request.path)  # todo TEST

        return super(GeneralLoginRequiredMixin, self).dispatch(request, *args, **kwargs)
