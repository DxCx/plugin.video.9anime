import urllib2
from urllib2 import URLError
import ssl
import httplib
import socket

class HeadRequest(urllib2.Request):
    def get_method(self):
        return "HEAD"

class HTTPRedirectHandler(urllib2.HTTPRedirectHandler):

    def http_error_302(self, req, fp, code, msg, headers):
        for no302 in noredirects:
            if no302.endswith("/") and no302 == req.get_full_url():
                if no302==req.get_full_url():
                    #return self.parent._open(req)
                    return (req, fp, 200, msg, headers)
            elif no302 in req.get_full_url():
                #return self.parent._open(req)
                return (req, fp, 200, msg, headers)
        else:
            result=urllib2.HTTPRedirectHandler.http_error_302(self,req, fp, code, msg, headers)
            result.status=code
            return result

    def http_error_301(self, *args,**kwargs):
        self.http_error_302(*args,**kwargs)

class HTTPErrorProcessor(urllib2.HTTPErrorProcessor):
    """Process HTTP error responses."""
    handler_order = 1000  # after all other processing

    def http_response(self, request, response):
        if response.code==302:
            for no302 in noredirects:
                if no302.endswith("/") and no302 == request.get_full_url():
                    if no302==request.get_full_url():
                        return response
                elif no302 in request.get_full_url():
                    return response
        return urllib2.HTTPErrorProcessor.http_response(self, request, response)

class NoCertSSLCon(httplib.HTTPConnection):
    default_port = httplib.HTTPS_PORT
    def __init__(self, *args, **kwargs):
        httplib.HTTPConnection.__init__(self, *args, **kwargs)

    def connect(self):
        #google app engine does not have source adress. r u drunk??
        if hasattr(self,"source_address"):
            sock = socket.create_connection((self.host, self.port), self.timeout, self.source_address)
        else:
            sock = socket.create_connection((self.host, self.port), self.timeout)

        if self._tunnel_host:
            self.sock = sock
            self._tunnel()
        self.sock = ssl.wrap_socket(sock,cert_reqs=ssl.CERT_NONE)

class HTTPSHandler(urllib2.HTTPSHandler):
    def __init__(self, *args, **kwargs):
        urllib2.HTTPSHandler.__init__(self, *args, **kwargs)

    def https_open(self, req):
        return self.do_open(NoCertSSLCon,req)

def send_request(url, data=None, set_request=None):
    if data:
        data = urllib.urlencode(data)
        req = urllib2.Request(url, data)
    else:
        req = urllib2.Request(url)

    opener = urllib2.build_opener(HTTPSHandler)
    req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36')
    if set_request:
        req = set_request(req)

    return opener.open(req)

def head_request(url, set_request=None):
    req = HeadRequest(url)
    opener = urllib2.build_opener(HTTPSHandler)
    req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36')
    if set_request:
        req = set_request(req)

    return opener.open(req)
