from threading import current_thread


class CurrentRequest(object):
    '''
    get_request can also be staticmethod
    '''
    _request_dict = {}

    @classmethod
    def get_request(cls):
        try:
            return cls._request_dict[current_thread()]
        except KeyError:
            return None

    def process_request(self, request):
        CurrentRequest._request_dict[current_thread()] = request

    def process_response(self, request, response):
        thread = current_thread()
        try:  # delete the request before sending response
            del CurrentRequest._request_dict[thread]
        except KeyError:
            pass
        return response


def get_current_request():
    return CurrentRequest.get_request()
