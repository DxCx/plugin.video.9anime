import re
import urllib
import urlparse
import utils
import http
import json
import time

from NineAnimeUrlExtender import NineAnimeUrlExtender
_EMBED_EXTRACTORS = {}

def load_video_from_url(in_url):
    found_extractor = None

    for extractor in _EMBED_EXTRACTORS.keys():
        if in_url.startswith(extractor):
            found_extractor = _EMBED_EXTRACTORS[extractor]
            break

    if found_extractor is None:
        print "[*E*] No extractor found for %s" % url
        return None

    try:
        if found_extractor['preloader'] is not None:
            print "Modifying Url: %s" % in_url
            in_url = found_extractor['preloader'](in_url)

        print "Probing source: %s" % in_url
        reqObj = http.send_request(in_url)
        page_content = reqObj.text
        url = reqObj.url

        return found_extractor['parser'](url, page_content)
    except http.URLError:
        return None # Dead link, Skip result
    except:
        raise

    return None

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

def __check_video_list(refer_url, vidlist):
    referer = __set_referer(refer_url)
    nlist = []
    for item in vidlist:
        try:
            temp_req = http.head_request(item[1], set_request=referer)
            nlist.append((item[0], temp_req.url))
        except Exception, e:
            # Just don't add source.
            pass

    return nlist

def __9anime_extract_direct(refer_url, grabInfo):
    # grabInfo['grabber'] sometimes ands with /?server=23 so we have to concat with & instead of ?
    url_parameter_concat = "&" if "?" in grabInfo['grabber'] else "?"
    url = "%s%s%s" % (grabInfo['grabber'], url_parameter_concat, urllib.urlencode(grabInfo['params']))
    url = __relative_url(refer_url, url)
    resp = json.loads(http.send_request(url,
                                        set_request=__set_referer(refer_url)).text)

    possible_error = resp['error'] if 'error' in resp.keys() else 'No-Error-Set'
    if 'data' not in resp.keys():
        if possible_error == 'deleted':
            return None
        raise Exception('Failed to parse 9anime direct with error: %s' %
                        resp['error'] if 'error' in resp.keys() else
                        'No-Error-Set')

    if 'error' in resp.keys() and resp['error']:
        print '[*E*] Failed to parse 9anime direct but got data with error: %s' % resp['error']

    return __check_video_list(refer_url, map(lambda x: (x['label'], x['file']), resp['data']))

def __preload_rapidvideo(url):
    return url + "?q=q"

def __extract_rapidvideo(url, page_content):
    SOURCES_RE = re.compile("<source\ssrc=\"([^\"]+)\"\s.+title=\"([^\"]+)\"\s.+?>")
    sources = SOURCES_RE.findall(page_content)
    return __check_video_list(url, map(lambda x: (x[1], x[0]), sources))

def __extract_9anime(url, page_content):
    episode_id = url.rsplit('/', 1)[1]
    url_info = urlparse.urlparse(url)
    domain = url_info.netloc
    scheme = url_info.scheme

    url_base = "%s://%s" % (scheme, domain)

    ts_value = NineAnimeUrlExtender.get_ts_value(page_content)
    extra_param = NineAnimeUrlExtender.get_extra_url_parameter(episode_id, 0, ts_value)

    url = "%s/ajax/episode/info?ts=%s&_=%d&id=%s&update=0" % (url_base, ts_value, extra_param, episode_id)

    time.sleep(0.3)
    urlRequest = http.send_request(url)

    grabInfo = json.loads(urlRequest.text)
    if 'error' in grabInfo.keys():
        raise Exception('error while trying to fetch info: %s' %
                        grabInfo['error'])
    if grabInfo['type'] == 'iframe':
        target = grabInfo['target']
        if target.startswith('//'):
            target = "%s:%s" % (url_info.scheme, target)

        return load_video_from_url(target)
    elif grabInfo['type'] == 'direct':
        return __9anime_extract_direct(url, grabInfo)

    raise Exception('Unknown case, please report')

def __animeram_factory(in_url, page_content):
    IFRAME_RE = re.compile("<iframe.+?src=\"(.+?)\"")
    embeded_url = IFRAME_RE.findall(page_content)[0]
    embeded_url = __relative_url(in_url, embeded_url)
    return load_video_from_url(embeded_url)

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

def __extract_with_urlresolver(url, content):
    # NOTE: Requires urlresolver dependancy (script.module.urlresolver) in
    # addon.xml

    import urlresolver
    return lambda: urlresolver.resolve(url)

def __extract_mycloud(url, content):
    playlist_url = re.findall("\"file\"\s*:\s*\"\/*(.+)\"", content)[0]
    if not playlist_url.startswith("http"):
        playlist_url = "https://" + playlist_url

    joinUrls = lambda x: (x[0], urlparse.urljoin(playlist_url, x[1]).rstrip())
    playlist_content = http.send_request(playlist_url, set_request=__set_referer(url)).text
    playlist_entries = re.findall("=\d*x(\d*)\n*([^#]*)\n*#?", playlist_content)
    playlist_entries_full = map(joinUrls, playlist_entries)
    return playlist_entries_full

# Thanks to https://github.com/munix/codingground
def __extract_openload(url, content):
    splice = lambda s, start, end: s[:start] + s[start + end:]

    ol_id = re.findall('<span[^>]+id=\"[^\"]+\"[^>]*>([0-9a-z]+)</span>', content)[0]
    arrow = ord(ol_id[0])
    pos = arrow - 52
    nextOpen = max(2, pos)
    pos = min(nextOpen, len(ol_id) - 30 - 2)
    part = ol_id[pos: pos + 30]
    arr = [0] * 10
    i = 0
    while i < len(part):
      arr[i / 3] = int(part[i: i + 3], 8)
      i += 3

    chars = [i for i in ol_id]
    chars = splice(chars, pos, 30)

    a = ''.join(chars)
    tagNameArr = []
    i = 0
    n = 0
    while i < len(a):
      text = a[i: i + 2]
      cDigit = a[i: i + 3]
      ch = a[i: i + 4]
      code = int(text, 16)
      i += 2
      if n % 3 is 0:
        code = int(cDigit, 8)
        i += 1
      else:
        if n % 2 is 0:
          if 0 is not n:
            if ord(a[n - 1][0]) < 60:
              code = int(ch, 10)
              i += 2

      val = arr[n % 9]
      code ^= 213
      code ^= val
      tagNameArr.append(chr(code))
      n += 1

    video_url = "https://openload.co/stream/" + ''.join(tagNameArr) + "?mime=true"
    return http.head_request(video_url).url

def __register_extractor(urls, function, url_preloader=None):
    if type(urls) is not list:
        urls = [urls]

    for url in urls:
        _EMBED_EXTRACTORS[url] = {
            "preloader": url_preloader,
            "parser": function,
        }

def __ignore_extractor(url, content):
    return None

def __relative_url(original_url, new_url):
    if new_url.startswith("http://") or new_url.startswith("https://"):
        return new_url

    if new_url.startswith("//"):
        return "http:%s" % new_url
    elif new_url.startswith("/"):
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

__register_extractor([
    "https://9anime.to/watch/",
    "https://9anime.tv/watch/",
    "https://9anime.is/watch/",

    "http://9anime.to/watch/",
    "http://9anime.tv/watch/",
    "http://9anime.is/watch/",
], __extract_9anime)

__register_extractor("http://ww1.animeram.cc", __animeram_factory)

__register_extractor("http://auengine.com/",
                    __extractor_factory("var\svideo_link\s=\s'(.+?)';"))

__register_extractor(["http://mp4upload.com/",
                      "http://www.mp4upload.com/",
                      "https://www.mp4upload.com/",
                      "https://mp4upload.com/"],
                    __extractor_factory("\"file\":\s\"(.+?)\","))

__register_extractor("http://videonest.net/",
                    __extractor_factory("\[\{file:\"(.+?)\"\}\],"))

__register_extractor(["http://animebam.com/", "http://www.animebam.net/"],
                    __extractor_factory("var\svideoSources\s=\s\[\{file:\s\"(.+?)\",", True))

__register_extractor(["http://yourupload.com/", "http://www.yourupload.com/", "http://embed.yourupload.com/"],
                     __extractor_factory("file:\s'(.+?\.mp4.*?)',", True))

__register_extractor("http://embed.videoweed.es/", __extract_swf_player)

__register_extractor("http://embed.novamov.com/", __extract_swf_player)

__register_extractor("https://openload.co/embed/", __extract_with_urlresolver)

__register_extractor(["https://mycloud.to/embed",
                      "http://mycloud.to/embed"],
                     __extract_mycloud)

__register_extractor(["https://www.rapidvideo.com/e/"],
                     __extract_rapidvideo,
                     __preload_rapidvideo)

# TODO: debug to find how to extract
__register_extractor("http://www.animeram.tv/files/ads/160.html", __ignore_extractor)
