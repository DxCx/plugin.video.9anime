import re
import urllib
import urlparse
import utils
import http

_EMBED_EXTRACTORS = {}

def __set_referer(url):
    def f(req):
        req.add_header('Referer', url)
        return req
    return f

def __set_flash(url):
    def f(req):
        req.add_header('X-Requested-With', 'ShockwaveFlash/19.0.0.226')
        return __set_referer(url)(req)
    return f

def load_video_from_url(in_url):
    IFRAME_RE = re.compile("<iframe.+?src=\"(.+?)\"")

    page_content = http.send_request(in_url).text
    embeded_url = IFRAME_RE.findall(page_content)[0]
    if embeded_url.startswith("//"):
        embeded_url = "http:%s" % embeded_url
    try:
        print "Probing source: %s" % embeded_url
        reqObj = http.send_request(embeded_url)
        page_content = reqObj.text
    except http.URLError:
        return None # Dead link, Skip result
    except:
        raise
    for extractor in _EMBED_EXTRACTORS.keys():
        if embeded_url.startswith(extractor):
            return _EMBED_EXTRACTORS[extractor](reqObj.url, page_content)
    print "[*E*] No extractor found for %s" % embeded_url
    return None

def _encode_data(data):
    encmap = ['.', '-']
    for old in encmap:
        data = data.replace(old, "%%%02X" % ord(old))
    return data

def __extract_js_var(content, name):
    value_re = re.compile("%s=\"(.+?)\";" % name, re.DOTALL)
    deref_re = re.compile("%s=(.+?);" % name, re.DOTALL)
    value = value_re.findall(content)
    if len(value):
        return value[0]

    deref = deref_re.findall(content)
    if not len(deref):
        return "undefined"
    return __extract_js_var(content, deref[0])

def __extract_swf_player(url, content):
    domain = __extract_js_var(content, "flashvars\.domain")
    assert domain is not "undefined"

    key = __extract_js_var(content, "flashvars\.filekey")
    filename = __extract_js_var(content, "flashvars\.file")
    cid, cid2, cid3 = ("undefined", "undefined", "undefined")
    user, password = ("undefined", "undefined")

    data = {
            'key': key,
            'file': filename,
            'cid': cid,
            'cid2': cid2,
            'cid3': cid3,
            'pass': password,
            'user': user,
            'numOfErrors': "0"
    }
    token_url = "%s/api/player.api.php?%s" % (domain, urllib.urlencode(data))

    video_info_res = http.send_request(token_url, set_request=__set_flash(url))
    video_info = dict(urlparse.parse_qsl(video_info_res.text))

    if video_info.has_key("error_msg"):
        print "[*] Error Message: %s" % (video_info["error_msg"])
    if not video_info.has_key("url"):
        return None
    return video_info['url']

def __register_extractor(urls, function):
    if type(urls) is not list:
        urls = [urls]

    for url in urls:
        _EMBED_EXTRACTORS[url] = function

def __ignore_extractor(url, content):
    return None

def __relative_url(original_url, new_url):
    if new_url.startswith("http://") or new_url.startswith("https://"):
        return new_url

    if new_url.startswith("/"):
        return urlparse.urljoin(original_url, new_url)
    else:
        raise Exception("Cannot resolve %s" % new_url)

def __extractor_factory(regex, double_ref=False, match=0, debug=False):
    compiled_regex = re.compile(regex, re.DOTALL)

    def f(url, content):
        if debug:
            print url
            print content
            print compiled_regex.findall(content)
            raise

        try:
            regex_url = compiled_regex.findall(content)[match]
            regex_url = __relative_url(url, regex_url)
            if double_ref:
                video_url = utils.head_request(regex_url, __set_referer(url)).url
            else:
                video_url = __relative_url(regex_url, regex_url)
            return video_url
        except Exception, e:
            print "[*E*] Failed to load link: %s: %s" % (url, e)
            return None
    return f

__register_extractor("http://auengine.com/",
                    __extractor_factory("var\svideo_link\s=\s'(.+?)';"))

__register_extractor("http://mp4upload.com/",
                    __extractor_factory("\"file\":\s\"(.+?)\","))

__register_extractor("http://videonest.net/",
                    __extractor_factory("\[\{file:\"(.+?)\"\}\],"))

__register_extractor(["http://animebam.com/", "http://www.animebam.net/"],
                    __extractor_factory("var\svideoSources\s=\s\[\{file:\s\"(.+?)\",", True))

__register_extractor(["http://yourupload.com/", "http://www.yourupload.com/", "http://embed.yourupload.com/"],
                     __extractor_factory("file:\s'(.+?\.mp4.*?)',", True))

__register_extractor("http://embed.videoweed.es/", __extract_swf_player)

__register_extractor("http://embed.novamov.com/", __extract_swf_player)

# TODO: debug to find how to extract
__register_extractor("http://www.animeram.tv/files/ads/160.html", __ignore_extractor)
