from http_imports import *

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

    def add_header(self, key, value):
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
    resp = __send_request(session, url, data, set_request, head)

    # Check if Cloudflare anti-bot is on
    if ( resp.status_code == 503
         and resp.headers.get("Server") == "cloudflare-nginx"
         and b"jschl_vc" in resp.content
         and b"jschl_answer" in resp.content
    ):
        return __solve_cf_challenge(session, resp, **{
            "data": data,
            "set_request": set_request,
            "head": head,
        })

    # Otherwise, no Cloudflare anti-bot detected
    return resp

def head_request(url, set_request=None):
    return send_request(url, set_request=set_request, head=True)

def __send_request(session, url, data=None, set_request=None, head=False):
    r = PrepReq()
    if set_request:
        r = set_request(r)

    kargs = {
        'headers': r.headers,
        'verify': False,
        'url': url,
        'allow_redirects': True,
    }

    if head:
        return session.head(**kargs)

    if data:
        data = urllib.urlencode(data)
        return session.post(data=data, **kargs)
    return session.get(**kargs)

#https://github.com/Anorov/cloudflare-scrape/blob/master/cfscrape/__init__.py#L47
def __extract_js(body):
    js = re.search(r"setTimeout\(function\(\){\s+(var "
                "s,t,o,p,b,r,e,a,k,i,n,g,f.+?\r?\n[\s\S]+?a\.value =.+?)\r?\n", body).group(1)
    js = re.sub(r"a\.value = (parseInt\(.+?\)).+", r"\1", js)
    js = re.sub(r"\s{3,}[a-z](?: = |\.).+", "", js)

    # Strip characters that could be used to exit the string context
    # These characters are not currently used in Cloudflare's arithmetic snippet
    js = re.sub(r"[\n\\']", "", js)

    return js

def __solve_cf_challenge(sess, resp, **original_kwargs):
    time.sleep(5)  # Cloudflare requires a delay before solving the challenge

    body = resp.text
    parsed_url = urlparse(resp.url)
    domain = urlparse(resp.url).netloc
    submit_url = "%s://%s/cdn-cgi/l/chk_jschl" % (parsed_url.scheme, domain)

    cloudflare_kwargs = {}
    params = cloudflare_kwargs.setdefault("params", {})
    headers = cloudflare_kwargs.setdefault("headers", {})
    headers["Referer"] = resp.url

    try:
        params["jschl_vc"] = re.search(r'name="jschl_vc" value="(\w+)"', body).group(1)
        params["pass"] = re.search(r'name="pass" value="(.+?)"', body).group(1)

        # Extract the arithmetic operation
        js = __extract_js(body)

    except Exception:
        # Something is wrong with the page.
        # This may indicate Cloudflare has changed their anti-bot
        # technique. If you see this and are running the latest version,
        # please open a GitHub issue so I can update the code accordingly.
        #logging.error("[!] Unable to parse Cloudflare anti-bots page. "
        #     "Try upgrading cloudflare-scrape, or submit a bug report "
        #     "if you are running the latest version. Please read "
        #     "https://github.com/Anorov/cloudflare-scrape#updates "
        #     "before submitting a bug report.")
        raise

    # Safely evaluate the Javascript expression
    params["jschl_answer"] = str(int(js2py.eval_js(js)) + len(domain))

    # Requests transforms any request into a GET after a redirect,
    # so the redirect has to be handled manually here to allow for
    # performing other types of requests even as the first request.
    method = resp.request.method
    cloudflare_kwargs["allow_redirects"] = False
    redirect = sess.request(method, submit_url, **cloudflare_kwargs)
    return __send_request(sess, redirect.headers["Location"], **original_kwargs)
