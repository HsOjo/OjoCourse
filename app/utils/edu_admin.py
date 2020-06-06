import requests


class EduAdmin:
    URL_FACE = '/cet/img/img/%s.jpg'

    def __init__(self, host, auth=None, protocol='http'):
        self._host = host
        self._protocol = protocol

        self._session = requests.session()
        self._session.auth = auth

    def _g_url(self, url):
        return '%s://%s/%s' % (self._protocol, self._host, url)

    def get_face(self, number):
        try:
            resp = self._session.get(self._g_url(self.URL_FACE % number))
            return resp.content
        except:
            return None
