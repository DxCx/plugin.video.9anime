import urllib2
from urllib2 import URLError
import httplib
import socket

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import ssl

_USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'
_SESSION = None

class SSLAdapter(HTTPAdapter):
    '''An HTTPS Transport Adapter that uses an arbitrary SSL version.'''
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                              maxsize=maxsize,
                              block=block)

class PrepReq(object):
    def __init__(self):
        self._dict = {}

    def add_headers(self, key, value):
        self._dict[key] = value

    @property
    def headers(self):
        return self._dict

def Session():
    global _SESSION
    if not _SESSION:
        s = requests.Session()
        s.mount('https://', SSLAdapter())
        s.headers.update({
            'User-Agent': _USER_AGENT,
        })
        _SESSION = s

    return _SESSION

def send_request(url, data=None, set_request=None, head=False):
    session = Session()
    r = PrepReq()
    if set_request:
        r = set_request(r)

    kargs = {
        'headers': r.headers,
        'verify': False,
        'url': url,
    }

    if head:
        return session.head(**kargs)

    if data:
        data = urllib.urlencode(data)
        return session.post(data=data, **kargs)
    return session.get(**kargs)

def head_request(url, set_request=None):
    return send_request(url, set_request=set_request, head=True)
