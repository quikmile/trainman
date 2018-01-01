import base64

import requests
from django.conf import settings


class Gitlab:
    headers = {'PRIVATE-TOKEN': settings.GITLAB_ACCESS_TOKEN}

    @classmethod
    def get(cls, path):
        r = requests.get(settings.GITLAB_API + path, headers=cls.headers)
        return r.json()

    @staticmethod
    def decode_content(coded_string, decoder='base64'):
        if decoder == 'base64':
            return base64.b64decode(coded_string)
