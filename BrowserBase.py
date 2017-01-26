import urllib
import http

class BrowserBase(object):
    _BASE_URL = None

    def _to_url(self, url=''):
        assert self._BASE_URL is not None, "Must be set on inherentance"

        if url.startswith("/"):
            url = url[1:]
        return "%s/%s" % (self._BASE_URL, url)

    def _send_request(self, url, data=None):
        return http.send_request(url, data).text

    def _post_request(self, url, data={}):
        return self._send_request(url, data)

    def _get_request(self, url, data=None):
        if data:
            url = "%s?%s" % (url, urllib.urlencode(data))
        return self._send_request(url)
