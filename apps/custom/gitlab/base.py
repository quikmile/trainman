import base64

import requests
from django.conf import settings


class Gitlab:
    headers = {'PRIVATE-TOKEN': settings.GITLAB_ACCESS_TOKEN}

    @classmethod
    def get(cls, path):
        api = settings.GITLAB_API + path
        print("request: {}".format(api))
        r = requests.get(api, headers=cls.headers)
        if r.status_code == 200:
            return r.json()
        else:
            raise Exception("gitlab api error: {}".format(r.text))

    @staticmethod
    def decode_content(coded_string, decoder='base64'):
        if decoder == 'base64':
            return base64.b64decode(coded_string)
